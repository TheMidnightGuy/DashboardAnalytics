#¿Que hace el parser? 
# Transforma el texto en formato a JSON a un objeto para que se pueda usar en programación.
# En este caso, para que lo consuma streamlit y represente los datos.

#Creamos la función 'parsear_drift' la cual crea un diccionario que recibe los datos del json que carga el usuario.

def parsear_drift(raw: dict) -> dict:

    resultado = {
        "dataset":  {}, #Recibe las metricas generales del dataset
        "columnas": {}  #Recibe las metricas individuales
    }

    #Itera sobre la lista 'metrics' y recibe los datos
    # Cada columna tiene una estructura con datos
    for m in raw["metrics"]:
        nombre = m["metric_name"]       #El nombre de la columna
        config = m.get("config", {})    #el diccionario de cada columna
        value  = m["value"]             #el valor de la metrica

        # -- Resumen global del dataset --
        if "DriftedColumnsCount" in nombre:
            total_columnas = len([
                x for x in raw["metrics"]
                if "ValueDrift" in x["metric_name"]
            ])
            resultado["dataset"] = {
                "n_drifted":      int(value["count"]),
                "drift_share":    round(value["share"], 4),
                "n_total":        total_columnas,
                # drift detectado si al menos 1 columna supera umbral
                "drift_detected": int(value["count"]) > 0,
            }

        # -- Drift por columna --
        if "ValueDrift" in nombre:
            col       = config["column"]
            threshold = config["threshold"]
            score     = round(float(value), 4)

            resultado["columnas"][col] = {
                "drift_score":    score,
                "drift_detected": score > threshold,
                "stattest":       config["method"],
                "threshold":      threshold,
                # p_value no viene en esta versión de la API
                "p_value":        None,
            }

    return resultado

def parsear_quality(raw: dict) -> dict:

    resultado = {
        "resumen":   {},   # métricas globales del dataset
        "nulos":     {},   # nulos por columna
        "numericas": {},   # estadísticos por columna numérica
        "categoricas": {}, # distribución por columna categórica
        "tests":     [],   # resultados de tests FAIL
    }

    for m in raw["metrics"]:
        nombre = m["metric_name"]
        config = m.get("config", {})
        value  = m["value"]

        # ── Resumen global ─────────────────────────────────
        if nombre == "RowCount()":
            resultado["resumen"]["n_filas"] = int(value)

        elif nombre == "ColumnCount()":
            resultado["resumen"]["n_columnas"] = int(value)

        elif "ColumnCount(column_type=ColumnType.Numerical)" in nombre:
            resultado["resumen"]["n_numericas"] = int(value)

        elif "ColumnCount(column_type=ColumnType.Categorical)" in nombre:
            resultado["resumen"]["n_categoricas"] = int(value)

        elif nombre == "DuplicatedRowCount()":
            resultado["resumen"]["filas_duplicadas"] = int(value)

        elif nombre == "AlmostConstantColumnsCount()":
            resultado["resumen"]["cols_casi_constantes"] = int(value)

        elif nombre == "EmptyRowsCount()":
            resultado["resumen"]["filas_vacias"] = int(value)

        elif nombre == "EmptyColumnsCount()":
            resultado["resumen"]["cols_vacias"] = int(value)

        elif nombre == "DatasetMissingValueCount()":
            resultado["resumen"]["nulos_total"]     = int(value["count"])
            resultado["resumen"]["nulos_share"]     = round(value["share"], 4)

        # ── Nulos por columna ──────────────────────────────
        elif "MissingValueCount(column=" in nombre:
            col = config.get("column")
            if col:
                resultado["nulos"][col] = {
                    "count": int(value["count"]),
                    "share": round(value["share"], 4),
                }

        # ── Estadísticos numéricos ─────────────────────────
        elif "MinValue(column=" in nombre:
            col = config.get("column")
            if col:
                resultado["numericas"].setdefault(col, {})["min"] = value

        elif "MaxValue(column=" in nombre:
            col = config.get("column")
            if col:
                resultado["numericas"].setdefault(col, {})["max"] = value

        elif "MeanValue(column=" in nombre:
            col = config.get("column")
            if col:
                resultado["numericas"].setdefault(col, {})["mean"] = round(value, 4)

        elif "StdValue(column=" in nombre:
            col = config.get("column")
            if col:
                resultado["numericas"].setdefault(col, {})["std"] = round(value, 4)

        elif "QuantileValue(column=" in nombre:
            col      = config.get("column")
            quantile = config.get("quantile")
            if col and quantile is not None:
                resultado["numericas"].setdefault(col, {})
                if quantile == 0.25:
                    resultado["numericas"][col]["p25"] = value
                elif quantile == 0.5:
                    resultado["numericas"][col]["p50"] = value
                elif quantile == 0.75:
                    resultado["numericas"][col]["p75"] = value

        # ── Valores únicos categóricas ─────────────────────
        elif "UniqueValueCount(column=" in nombre:
            col = config.get("column")
            if col:
                resultado["categoricas"][col] = {
                    "counts": value.get("counts", {}),
                    "shares": value.get("shares", {}),
                }

    # ── Tests fallidos ─────────────────────────────────────
    # Solo guardamos los FAIL para mostrar en alertas
    for t in raw.get("tests", []):
        if t["status"] == "FAIL":
            resultado["tests"].append({
                "nombre":      t["name"],
                "descripcion": t["description"],
                "critico":     t["test_config"].get("is_critical", False),
            })

    return resultado


def parsear_model(raw: dict) -> dict:

    resultado = {
        "resumen":    {},   # métricas globales (accuracy, precision, recall, f1, tpr, tnr, fpr, fnr)
        "por_clase":  {},   # métricas desglosadas por clase (f1, precision, recall)
        "tests":      [],   # resultados de tests FAIL
    }

    # Mapa de nombre corto -> clave en metric_name de Evidently
    metricas_globales = {
        "accuracy":  "Accuracy(",
        "precision": "Precision(",
        "recall":    "Recall(",
        "f1":        "F1Score(",
        "tpr":       "TPR(",
        "tnr":       "TNR(",
        "fpr":       "FPR(",
        "fnr":       "FNR(",
    }

    metricas_por_clase = {
        "f1":        "F1ByLabel(",
        "precision": "PrecisionByLabel(",
        "recall":    "RecallByLabel(",
    }

    for m in raw["metrics"]:
        nombre = m["metric_name"]
        value  = m["value"]

        # ── Métricas globales (valor escalar) ──────────────
        for clave, patron in metricas_globales.items():
            if patron in nombre and "ByLabel" not in nombre:
                if isinstance(value, (int, float)):
                    resultado["resumen"][clave] = round(float(value), 4)
                break

        # ── Métricas por clase (valor dict) ────────────────
        for clave, patron in metricas_por_clase.items():
            if patron in nombre:
                if isinstance(value, dict):
                    resultado["por_clase"][clave] = {
                        str(k): round(float(v), 4) for k, v in value.items()
                    }
                break

    # ── Tests fallidos ─────────────────────────────────────
    for t in raw.get("tests", []):
        if t.get("status") == "FAIL":
            resultado["tests"].append({
                "nombre":      t["name"],
                "descripcion": t["description"],
                "critico":     t.get("test_config", {}).get("is_critical", False),
            })

    return resultado