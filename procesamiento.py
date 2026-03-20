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

load_file = "data/uploaded.csv"
df_upload = pd.read_csv(load_file)
print("Dataset cargado correctamente")

#============================
#     Drift artificial 
#============================
#Se crea un dataset a partir del original.
# Si la variable es categórica  == object: 
#   obtiene el nombre de los valores dentro de una columna y los reemplaza por un valor aleatorio.

# Si la variable es numérica    == int64:  
#   obtiene el nombre de los valores dentro de una columna y los reemplaza por un valor aleatorio.
#   se agrega ruido gaussiano: los valores se agrupan en torno a la media y se le agrega una pequeña varianza.

df_drift = df_upload.copy()

for col in df_drift.columns:
    if df_drift[col].dtype == 'object':
        unique_vals = df_drift[col].dropna().unique()
        df_drift.loc[df_drift.sample(frac=0.2).index, col] = np.random.choice(unique_vals)
    elif df_drift[col].dtype == 'int64':
        df_drift.loc[df_drift.sample(frac=0.2).index, col] += np.random.normal(
            0, df_drift[col].std() * 0.5
        )

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

data_drift_report.save_html("reports/data_drift/data_drift_report.html")
data_drift_report.save_json("data/snapshots/data_drift_report.json")

print("Archivos exportados correctamente")