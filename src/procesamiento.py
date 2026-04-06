#procesamiento.py

#Lógica extraida de notebook desarrollado en Google Colab.

#Dentro de este archivo se lleva a cabo el segúndo procesamiento.
#Reporte/Vistas generadas a partir de procesamiento.py
"""
1. Reporte - Data Drift
2. Reporte - Data Quality
3. Dashboard - Data Drift
4. Dashboard - Data Quality
"""

#Flujo de usuario - app.py/procesamiento.py
"""
1. Se aplica una lógica de decisión para evaluar la calidad de los datos.
2. Se selecciona modelo de ML para entrenamiento y permite selección de columnas features asi como target.
3. Se entrena modelo de ML en base a los parametros seleccionados por el usuario
"""

#Prerequisitos:
# Ya contar con las dependencias del proyecto instaladas a partir de poetry.

#importamos librerias y sus componentes correspondientes
#base
import pandas as pd
import numpy as np

#evidently
import evidently
from evidently import Dataset,DataDefinition, Report
from evidently.presets import ClassificationPreset

#sistema - para interacturar con directorios
import os 

#============================
# Directorios de exportación 
#============================
#Creamos los directorios en caso de que no existan.
#(Necesario para app dockerizada sin un volumen definido.)

#Reportes HTML: reports/model_performance
#Reportes JSON: data/snapshots
#Modelos ML:    models/...

os.makedirs("models",                     exist_ok=True)
os.makedirs("reports/model_performance",  exist_ok=True) 
os.makedirs("data/snapshots",             exist_ok=True)


#============================
# Lógica de decisión 
#============================
#Nos preguntamos.. ¿Es buena la calidad de los datos?
# para evaluar la calidad de los datos tenemos de referencia las metricas de los reportes de:
# data quality y data drift. 
# A partir de los umbrales definidos extraidos del reporte en formato JSON podemos definir la calidad de los datos y tomar una decisión,
#Si la calidad de los datos es buena podemos reentrenar modelo con nuevo conjunto de datos.
#Si la calidad de los datos es mala se modifican los datos y se vuelve a evaluar y generar un reporte.

#Si bien se aplica la lógica de manera interna para decidir si se autoriza y realiza un reentrenamiento al modelo podemos permitir que el usuario revise y autorice de manera manual previo reentrenamiento en caso de existir algún error.
#============================
# Seleccion de modelo ML
#============================
#Dentro de esta sección el usuario podra seleccionar que modelo de ML usar junto con las features 

#============================
#  Reporte Model Performance
#============================
#Se usa ClassificationPreset para generar métricas de rendimiento del modelo.
#Se detecta la última columna binaria/categórica como target y se entrena un clasificador simple.

print("Generando reporte Model Performance...")

model_perf_generado = False

# Buscar columna target: última columna binaria (2 valores únicos)
target_col = None
for col in reversed(df_upload.columns):
    n_unique = df_upload[col].dropna().nunique()
    if n_unique == 2:
        target_col = col
        break

if target_col is not None:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import LabelEncoder
    from evidently.core.datasets import BinaryClassification

    print(f"Target detectado: '{target_col}'")

    # Preparar datos: separar features numéricas y target
    feature_cols = [c for c in numerical if c != target_col]

    if len(feature_cols) > 0:
        # Codificar target si es categórico
        le = LabelEncoder()
        y_ref = le.fit_transform(df_upload[target_col].fillna(df_upload[target_col].mode().iloc[0]))
        y_act = le.transform(df_drift[target_col].fillna(df_drift[target_col].mode().iloc[0]))

        X_ref = df_upload[feature_cols].fillna(0)
        X_act = df_drift[feature_cols].fillna(0)

        # Entrenar modelo simple sobre referencia
        modelo = LogisticRegression(max_iter=500, random_state=42)
        modelo.fit(X_ref, y_ref)

        # Predecir sobre ambos datasets
        df_ref_model = df_upload.copy()
        df_act_model = df_drift.copy()
        df_ref_model["target"]     = y_ref
        df_ref_model["prediction"] = modelo.predict(X_ref)
        df_act_model["target"]     = y_act
        df_act_model["prediction"] = modelo.predict(X_act)

        # Schema para clasificación
        model_schema = DataDefinition(
            numerical_columns=feature_cols,
            categorical_columns=categorical + ["target", "prediction"],
            classification=[BinaryClassification(
                target="target",
                prediction_labels="prediction",
            )],
        )

        ds_ref_model = Dataset.from_pandas(df_ref_model, data_definition=model_schema)
        ds_act_model = Dataset.from_pandas(df_act_model, data_definition=model_schema)

        # Generar reporte
        report_model_perf = Report([ClassificationPreset()])
        model_perf_report = report_model_perf.run(ds_act_model, ds_ref_model)

        model_perf_report.save_json("data/snapshots/model_performance_report.json")
        print("JSON exportado Model Performance")

        model_perf_report.save_html("reports/model_performance/model_perform_report.html")
        print("HTML exportado Reporte Model Performance")

        model_perf_generado = True
    else:
        print("No hay columnas numéricas para features — Model Performance omitido")
else:
    print("No se detectó columna target binaria — Model Performance omitido")

if not model_perf_generado:
    print("Model Performance: sin reporte generado en esta ejecución")