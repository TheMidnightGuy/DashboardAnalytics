#logica extraida de notebook desarrollado en google colab.
#Se consevaron las siguentes fases necesarias para la construcción de los reportes en evidently.

#Prerequisitos:
# Ya contar con las dependencias del proyecto instaladas a partir de poetry.

#Importamos librerias y sus componentes correspondientes
import pandas as pd
import numpy as np

#Evidently
from evidently import Dataset, DataDefinition, Report
from evidently.presets import DataDriftPreset

#sistema - para interactuar con directorios
import os

#============================
# Directorios de exportación 
#============================
#Creamos los directorios en caso de que no existan.
#(Necesario para app dockerizada sin un volumen definido.)

#Reportes html: reports/data_drift
#Reportes json: data/snapshots

os.makedirs("reports/data_drift", exist_ok=True) 
os.makedirs("data/snapshots",     exist_ok=True)

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

report           = Report([DataDriftPreset()])
data_drift_report = report.run(dataset_act, dataset_ref)

print("Reporte generado correctamente")

#============================
#       Exportar 
#============================
#Guardamos los archivos para ser consumidos por streamlit.

#reporte
data_drift_report.save_html("reports/data_drift/data_drift_report.html")
data_drift_report.save_json("data/snapshots/data_drift_report.json")
print("Reporte exportado")

#dataset modificado
df_drift.to_csv("data/modified.csv", index=False)

df_modified = pd.read_csv("data/modified.csv")
print(df_modified.dtypes)
print(df_modified.shape)

print("Dataset exportado")

print("Archivos exportados correctamente")