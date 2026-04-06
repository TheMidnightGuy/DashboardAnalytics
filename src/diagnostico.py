#diagnostico.py

#Lógica extraida de notebook desarrollado en googlecolab.

#Dentro de este archivo se llevaran a cabo el procesamiento inicial.
#Reporte/Vistas generadas a partir de diagnostico.py
"""
1. Reporte - Data Drift
2. Reporte - Data Quality
3. Dashboard - Data Drift
4. Dashboard - Data Quality
"""

#Flujo de usuario - app.py/diagnostico.py

"""
1. Usuario sube archivo CSV (app.py).
2. Se realiza un procesamiento interno de los datos (diagnostico.py).
3. Usuario ve reflejado los reportes generados por evidently y las metricas interactivas en el dashboard (app.py).
"""

#Flujo de desarrollo - diagnostico.py
"""
1. Se crean directorios en el proyecto para guardar reportes exportados en HTML y JSON.
2. Se realiza carga de dataset (se espera input del usuario).
3. Se realiza la verificación de la condición para gran volumen de datos (CSV > 20.000 filas).
4. Se aplica drift artificial para generar una comparación con data historica (Con fines de Prueba de concepto).
5. Se agrupan las columnas por tipo de dato (cat/num) y se crea un esquema.
6. Se crean los datasets de evidently para generar los reportes
7. Se generar los reportes de Data Drift y Data Quality asi como sus vistas en el dashboard.
8. Se exporta el JSON del reporte preservando todos los datos.
9. Se exporta el HTML del reporte en una muestra más pequeña de los datos preservando la calidad de los mismos.
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
from evidently.presets import DataDriftPreset, DataSummaryPreset

#sistema - para interacturar con directorios
import os 

#============================
# Directorios de exportación 
#============================
#Creamos los directorios en caso de que no existan.
#(Necesario para app dockerizada sin un volumen definido.)

#Reportes html: reports/data_drift
#Reportes json: data/snapshots

os.makedirs("reports/data_drift",         exist_ok=True) 
os.makedirs("reports/data_quality",       exist_ok=True)
os.makedirs("data/snapshots",             exist_ok=True)

#============================
#     Carga del dataset 
#============================
#Dentro de la lógica de streamlit al cargar un archivo este se guarda en 'data/uploaded.csv'.

print("Cargando dataset...")

load_file = "data/uploaded.csv"
df_upload = pd.read_csv(load_file)
print("Tipos de datos:")
print("========================")
print(df_upload.dtypes)
print("========================")
print("N° de filas y columnas:")
print(df_upload.shape)
print("========================")
print(df_upload)
print("Dataset cargado correctamente")

#============================
#     Limite de dataset 
#============================
#TESTING: Se limita el número de filas del dataset en caso de ser un número elevado (>=10000).
# Esto debido a que evidently se ve limitado ante una ingesta de datos en gran volumen a la hora de generar el reporte.

print("Verificando condiciones de limite...")

LIMIT = 20000

#Se definen condiciones para aplicar limite en el dataset
# Se muestran a traves del output si se aplicaron cambios
if len(df_upload) > LIMIT:
    df_upload = df_upload.sample(n=LIMIT ,random_state=42)
    print(f"Limite aplicado a: {LIMIT} filas")
else:
    print(f"No se ha modificado el dataset. {len(df_upload)} filas")

#============================
#     Drift artificial 
#============================
#Se crea un dataset a partir del original.
# Si la variable es categórica  == object: 
#   obtiene el nombre de los valores dentro de una columna y los reemplaza por un valor aleatorio.

# Si la variable es numérica    == int64:  
#   obtiene el nombre de los valores dentro de una columna y los reemplaza por un valor aleatorio.
#   se agrega ruido gaussiano: los valores se agrupan en torno a la media y se le agrega una pequeña varianza.

print("Aplicando drift artificial...")

df_drift = df_upload.copy()

for col in df_drift.columns:
    if df_drift[col].dtype.name in ['object', 'category', 'bool']:
        unique_vals = df_drift[col].dropna().unique()
        if len(unique_vals) > 1:
            df_drift.loc[df_drift.sample(frac=0.2).index, col] = np.random.choice(unique_vals)

    elif df_drift[col].dtype.name in ['int64', 'float64', 'int32']:
        std = df_drift[col].std()
        if std > 0:
            idx = df_drift.sample(frac=0.2).index
            ruido = np.random.normal(0, std * 0.5, size=len(idx))

            ruido = ruido.astype(df_drift[col].dtype)

            df_drift.loc[idx, col] += ruido



print("Tipos de datos:")
print("========================")
print(df_drift.dtypes)
print("========================")
print("N° de filas y columnas:")
print(df_drift.shape)
print("========================")
print(df_drift)

print("Drift artificial generado")

#============================
#           Schema
#============================
#Agrupamos las columnas por tipo de dato.

numerical   = df_drift.select_dtypes(include=["int64", "float64", "int32"]).columns.to_list()
categorical = df_drift.select_dtypes(include=["object", "category", "bool"]).columns.to_list()

schema = DataDefinition(
    numerical_columns=numerical,
    categorical_columns=categorical
)
#============================
#   Datasets Evidently 
#============================
#Se crean nuevos dataset a partir del dataset original y el dataset con drift artificial en los datos,

dataset_act = Dataset.from_pandas(pd.DataFrame(df_drift),    data_definition=schema)
dataset_ref = Dataset.from_pandas(pd.DataFrame(df_upload),   data_definition=schema)

#============================
#   Reporte Data Drift
#============================
#Usamos el preset 'DataDriftPreset' a partir de los datasets evidently.

report_data_drift          = Report([DataDriftPreset()])
data_drift_report = report_data_drift.run(dataset_act, dataset_ref)

print("Reporte generado correctamente")

#============================
#   Reporta Data Quality
#============================

report_data_quality        = Report([DataSummaryPreset()])
data_quality_report = report_data_quality.run(dataset_act, dataset_ref)

#============================
#   Exportar JSON (completo)
#============================
#Guardamos el JSON con datasets completos para que el dashboard lo consuma via parser.

data_drift_report.save_json("data/snapshots/data_drift_report.json")
print("JSON exportado Data Drift (datasets completos)")

data_quality_report.save_json("data/snapshots/data_quality_report.json")
print("JSON exportado Data Quality (datasets completos)")

#============================
#   Muestras para reporte 
#============================
#Creamos muestras a partir de los datasets completos.
#El reporte HTML se genera con muestras para mejorar rendimiento de Evidently.

print("Creando muestras...")

SAMPLE_SIZE = 5000

n_sample = min(SAMPLE_SIZE, len(df_upload))
df_sample_ref = df_upload.sample(n=n_sample, random_state=42)
df_sample_act = df_drift.sample(n=n_sample, random_state=42)

print(f"Muestras creadas: {n_sample} filas cada una")

#============================
#  Evidently con muestras
#============================
#Se ejecuta Evidently usando las muestras para generar el reporte HTML.

dataset_sample_act = Dataset.from_pandas(pd.DataFrame(df_sample_act), data_definition=schema)
dataset_sample_ref = Dataset.from_pandas(pd.DataFrame(df_sample_ref), data_definition=schema)

drift_report_sample            = Report([DataDriftPreset()])
data_drift_report_sample = drift_report_sample.run(dataset_sample_act, dataset_sample_ref)

quality_report_sample          = Report([DataSummaryPreset()])
data_quality_report_sample = quality_report_sample.run(dataset_act, dataset_ref)

print("Reporte con muestras generado correctamente")

#============================
#  Exportar HTML (muestras)
#============================
#Guardamos el HTML generado con muestras.

data_drift_report_sample.save_html("reports/data_drift/data_drift_report.html")
print(f"HTML exportado Reporte Drift (muestras)")

data_quality_report_sample.save_html("reports/data_quality/data_quality_report.html")
print("HTML exportado Reporte Quality (muestras)")

#============================
#   Exportar muestras CSV
#============================
#Se exportan ambas muestras para visualizar bajo reporte.

os.makedirs("data/samples", exist_ok=True)
df_sample_ref.to_csv("data/samples/sample_ref.csv", index=False)
df_sample_act.to_csv("data/samples/sample_act.csv", index=False)
print("Muestras exportadas")

#============================
#  Exportar dataset modificado
#============================
#Guardamos la muestra del dataset con drift artificial.

df_sample_act.to_csv("data/modified.csv", index=False)

df_modified = pd.read_csv("data/modified.csv")
print(df_modified.dtypes)
print(df_modified.shape)

print("Dataset exportado")

print("Archivos exportados correctamente")