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
    page_title= 'EVIDENTLY - Dashboard Analytics',
    page_icon="📉",
    layout="wide"
)

#Parser JSON

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

#===== BARRA LATERAL ======
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
        ("DataDrift","DataQuality","ModelPerformance"),
        index=None,
        placeholder="Selecciona tipo"
    )
    #--- Sección acciones ---
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

    #--- Sección carga de archivos ----
        #Header carga de archivos
    st.write("---------------")
    st.subheader("Carga de archivos")
    #Cargar archivos CSV
    #Usuario carga dataset
    upload_file_csv = st.file_uploader(label="**Cargar dataset**",
                                   max_upload_size=10,
                                   type="csv")
    if upload_file_csv is not None:
        dataframe_upload = pd.read_csv(upload_file_csv)

    #Cargar archivos JSON
    #Usuario carga snapshots
    upload_file_json = st.file_uploader(label='**Cargar snapshot**',
                                        max_upload_size=10,
                                        type="json")



    #--- Sección Exportar ---
    st.write("---------------")

    #Subheader exporta (según vista)
    if vista=="Dashboard":    
        st.subheader("Exportar Dashboard")
    elif vista=="Reporte":
        st.subheader("Exportar Reporte")

    #Formato a exportar (PDF)

    formato_exp = st.selectbox(
        "Formato",
        ("PDF"),
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



#--- Rendimiento detallado ---
#Curva roc, matriz de confusión, Importance de features

#--- Alertas definidas  ---
# Reglas de configuración -> st.warning, st.error
# Las alertas se deben configurar en base a los parametros de detección de drift del modelo

#--- Resumen de los datos utilizados ---
#Fuente de datos: dataset
#etc...

    

#===== VISTAS ======

#--- Reporte Data Drift ---
if vista=="Reporte" and tipo_reporte=="DataDrift":
    with open("reports/data_drift/datadrift_report.html", 'r', encoding='utf-8') as f:
        html_data_drift = f.read()
        st.components.v1.html(html_data_drift, height=2000, scrolling=True)

#--- Reporte Data Quality ---
if vista=="Reporte" and tipo_reporte=="DataQuality":
    with open("reports/data_quality/data_quality_report.html", 'r', encoding="utf-8") as f:
        html_data_quality = f.read()
        st.components.v1.html(html_data_quality, height=2000, scrolling=True)

if vista=="Reporte" and tipo_reporte=="ModelPerformance":
    with open("reports/model_performance/model_perform_report.html", 'r', encoding="utf-8") as  f:
        html_model_perf = f.read()
        st.components.v1.html(html_model_perf, height=2000, scrolling=True)

if vista=="Dashboard":

        #===== PAGINA ======

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

    #--- Selección tipo de reporte ---

    #Definimos pestañas
    tab1, tab2, tab3 = st.tabs(["Data Drift", "Data Quality", "Model Performance"])

    #Pestaña 1- Data drift
    with tab1:
    
        with st.container():
    #---- Alertas y resumen ----
            st.write ("**Alertas y resumen ejecutivo**")
            st.error('Alerta! Drift en dataset: 10% - umbral establecido en Max.7%', icon="🟥")
            st.warning('Advertencia! Drift en dataset: 5% - umbral establecido en Max.7%', icon="⚠️")

    #--- Metricas comunes del modelo ---
        with st.container():
            st.write("**KPIs**")
            
            #Creamos tres columnas, una para cada metrica (Accuracy, F1score, auc/roc)
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label="**Dataset drift**", value="Detectado", delta="5 columnas afectadas", delta_color="red", delta_arrow="off", border=True)

            with col2:
                st.metric(label="**Drift share**", value="14,9%", delta="3.2%", delta_color='red', border=True)

            with col3:
                st.metric(label="**Columnas con drift**", value="5/34", delta="2 nuevas columnas", delta_color="red", border=True)

            with col4:
                st.metric(label="**Umbral de Drift**",value="10,5%",  delta="4,4%", delta_color="red", delta_arrow="up", border=True)

            st.divider()

    #--- Gráficos ---
        #--- Análisis por columna ---
        with st.container():
            st.write("**Análisis por columna**")

            columnas = data["columnas"]

            #st.dataframe()
            

        #--- Dataset cargado ---
        #Dataframe utilizado: para cargar un dataset se deben seguir los mismos pasos que si se hiciera en un notebook.
        #cargamos dataset al final de la pagina 
        with st.container():
        #Header
            st.header("Dataset cargado")

            #Visualizamos
            if upload_file_csv is None:
                st.warning("Dataframe no se ha cargado aún")
            elif upload_file_csv is not None:
                st.dataframe(dataframe_upload)

    
    #Pestaña 2 - Data quality
    with tab2:
        
        col1, col2, col3, col4, col5 = st.columns(5)

        #Advertencias tras analizar datos del modelo
        st.write ("Alertas y resumen ejecutivo")
        st.error('Alerta! Nulos en dataset: 10% - umbral establecido en Max.7%', icon="🟥")
        st.warning('Advertencia! Nulos en dataset: 5% - umbral establecido en Max.7%', icon="⚠️")

        #
        

    #Pestaña 3 - Model Performance
    with tab3:
        st.write ("Model performance")







