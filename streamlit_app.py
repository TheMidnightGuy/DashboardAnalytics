#import
import streamlit as st
import streamlit.components.v1
import time as tm
import pandas as pd
import evidently
import datetime as dt


#--- Configuración de la página ---
#Defininimos titulo
#Definimos icono
#Ocupamos la totalidad de la pagina horizontalmente
st.set_page_config(
    page_title= 'Dashboard EvidentlyAI',
    page_icon="📉",
    layout="wide"
)

#--- CACHE DE LA APP ---
# -- Cache de data -- 
#   (@st.cache_data)
# Sirve para guardar objetos que pueden ser convertidos a texto.
# Ejemplos:
# - Archivos csv, excel, etc.
# - Consultas a BD
# - Schemas
# Crea una copia del objeto original

# -- Cache de recursos -- 
#  (@st.cache_resources)

# Sirve para guardar objetos que mantiene su formato original.
# Ejemplos:
# - Modelos ML
# - Conexiones a BD
# Mantiene el objeto original pero lo devuelve como una referencia.

#---Barra lateral---
with st.sidebar:
    #Imagen - logo EvidentlyAI
    st.image(image='https://cdn.prod.website-files.com/660ef16a9e0687d9cc2746d7/66180fbf4f40e9ed73ca2d39_evidently_ai_logo_fi.png')
    #Tipo de vista
    vista = st.selectbox(
        "Elige vista",
        ("Dashboard", "Reporte"),
        index=None,
        placeholder="Selecciona una vista"
    )
    #Tipo de reporte
    tipo_reporte = st.selectbox(
        "Tipo de reporte",
        ("DataDrift","Concept drift"),
        index=None,
        placeholder="Selecciona tipo"
    )
    #--- Sección Infomación ---
    #Header Actualizar info
    st.write("---------------")
    st.subheader("Acciones")

    #Obtener datetime actual para ver cuando se actualizo
    act_info_dt = dt.datetime.now()

    msg = st.empty()
    #Boton Actualizar info
    if st.button('Actualizar información'):
        msg.success('Actualizado correctamente')
        st.caption('Ultima vez actualizado: ',)
        st.write(act_info_dt.strftime("%c"))
        tm.sleep(3)
        msg.empty()
    else:
        st.caption('Ultima vez actualizado: ')
        
    #--- Sección Exportar ---
    st.write("---------------")

    #Subheader exporta (según vista)
    if vista=="Dashboard":    
        st.subheader("Exportar Dashboard")
    elif vista=="Reporte":
        st.subheader("Exportar Reporte")

    #Formato a exportar (JSON/HTML)

    formato_exp = st.selectbox(
        "Formato",
        ("JSON", "HTML"),
        index=None,
        placeholder="Selecciona formato"
    )

    #Boton exportar con barra de progreso
    if st.button("Exportar"):
        progress_txt = "Operación en progreso. Por favor espere."
        my_bar = st.progress(0, text=progress_txt)

        for percent_complete in range(100):
            tm.sleep(0.02)
            my_bar.progress(percent_complete + 1, text=progress_txt)
        tm.sleep(1)
        my_bar.empty()

#---Header Pagina---
#Nombre de Header depende de parametros seleccionados en barra lateral
 #llamamos a 'vista'
if vista=="Dashboard":
    st.header("Dashboard")
elif vista=="Reporte":
    st.header("Reporte")
else:
    st.header("Vista")

#--- Selector de modelo activo ---
#Todos estos componentes se encuentran dentro de un contenedor
#Juntamos los elementos dentro de una columna para organizarlos de manera horizontal

with st.container():

    col1 , col2 = st.columns(2)

    with col1:
        current_model = st.selectbox(
            "Modelo actual",
            ("Modelo RL","Modelo API"),
            index=None,
            placeholder="Seleccione modelo"
        )

    with col2:
        st.write("Estado:")
        st.badge("Activo", color="green")
        st.badge("En prueba", color="yellow")
        st.badge("Detenido", color="red")

#--- Metricas comunes del modelo ---
with st.container():
    
    #Creamos tres columnas, una para cada metrica (Accuracy, F1score, auc/roc)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Accuracy")
        st.metric(label="Accuracy", value="0.78", delta="+1.4%")

    with col2:
        st.write("F1-Score")
        st.metric(label="Accuracy", value="0.97", delta="+6 pts")

    with col3:
        st.write("AUC/ROC")
        st.metric(label="Accuracy", value="0.71", delta="-5 pts")

#--- Seleccionar tipo de Drift ---
# Tipos de drift: Data, Concept, Model Perf. Rendimiento general

import numpy as np
from numpy.random import default_rng as rng

df = pd.DataFrame(
    {
        "col1": list(range(20)) * 3,
        "col2": rng(0).standard_normal(60),
        "col3": ["a"] * 20 + ["b"] * 20 + ["c"] * 20,
    }
)

with st.container():

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("heatmap")
        st.line_chart(df, x="col1", y="col2", color="col3")


    with col2:
        st.subheader("Distribución ref vs actual")
        st.line_chart(df, x="col1", y="col2", color="col3")

#--- Rendimiento detallado ---
#Curva roc, matriz de confusión, Importance de features

#--- Alertas definidas  ---
# Reglas de configuración -> st.warning, st.error
# Las alertas se deben configurar en base a los parametros de detección de drift del modelo

#--- Resumen de los datos utilizados ---
#Fuente de datos: dataset
#etc...

    



#--- Reporte Data Drift ---
if vista=="Reporte" and tipo_reporte=="DataDrift":
    with open("reports/data_drift/datadrift_report.html", 'r', encoding='utf-8') as f:
        html_data = f.read()
        st.components.v1.html(html_data, height=2000, scrolling=True)










