#app.py

#imports
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import time as tm
import json
import subprocess
import sys

#importamos modulos y vistas
from core.parser import parsear_drift, parsear_quality

import vistas.data_drift as vista_drift
import vistas.data_quality as vista_quality

#======================
# Configuración Página
#======================
#Defininimos titulo
#Definimos icono
#Ocupamos la totalidad de la pagina horizontalmente
st.set_page_config(
    page_title= 'EVIDENTLY - Dashboard Analytics',
    page_icon="📉",
    layout="wide"
)

#======================
# Barra lateral
#======================

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

    if vista=="Reporte":
        tipo_reporte = st.selectbox(
            "Tipo de reporte",
            ("DataDrift","DataQuality(demo)","ModelPerformance(demo)"),
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

    dataframe_upload =None

    upload_file_csv= st.file_uploader(
        label="**Cargar dataset**",
        type="csv",
        max_upload_size=10
    )

    #Dataset hacia notebook evidently
    if upload_file_csv is not None:
        # lee y guarda el .csv
        dataframe_upload = pd.read_csv(upload_file_csv)
        dataframe_upload.to_csv("data/uploaded.csv", index=False)

        # Ejecutamos procesamiento.py 
        notebook = subprocess.run(
            [sys.executable, "procesamiento.py"],
            capture_output=True,
            text=True
        )

        #Una vez termino el flujo del notebook:
        #   lee el json generado para posteriormente parser.py lo procese
        if notebook.returncode == 0:
            with open ("data/snapshots/data_drift_report.json", "r", encoding="utf-8") as f:
                cargar_json = json.load(f)

            #Usamos 'st.session_state' para persistir variables entre ejecuciones de streamlit.
            #llamamos a la función de 'parser.py'.
            st.session_state["drift_data"] = parsear_drift(cargar_json)
            st.session_state["drift_nombre"] = "data_drift_report.json"
    
    else:
        #Si se quita el csv cargado eliminamos la data que persiste. (usamos .pop)
        #(drift_data / drift_nombre)
        st.session_state.pop("drift_data", None)
        st.session_state.pop("drift_nombre", None)

    #--- Boton para descargar csv ---

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
        ("HTML"),
        index=None,
        placeholder="Selecciona formato"
    )

    #Boton exportar con barra de progreso
    #Descargar Reporte
    if vista=="Reporte" and tipo_reporte=="DataDrift" and formato_exp=="HTML":

        #Leemos html para que boton lo lea
        with open("reports/data_drift/data_drift_report.html", 'r', encoding="utf-8") as f:
            report_html_drift = f.read()

        #Boton de descarga
        report_btn = st.download_button(
            label       = "Exportar reporte",
            data        = report_html_drift,
            file_name   = "data_drift_report.html",
            mime        = 'text/html'
        )

        if report_btn:
            #Descargar reporte actual
        
            #Barra de progreso
            progress_txt = "Operación en progreso. Por favor espere."
            my_bar = st.progress(0, text=progress_txt)

            for percent_complete in range(100):
                tm.sleep(0.02)
                my_bar.progress(percent_complete + 1, text=progress_txt)
            tm.sleep(1)
            my_bar.empty()

    #Descargar Dashboard




#======================
#Vista - Reporte
#======================
if vista=="Reporte":
    
    st.header("Reporte")

    #Si no se ha cargado dataset mostrar mensaje
    if upload_file_csv is None:
            #entrega un mensaje en pantalla
            st.info("Carga dataset en formato CSV desde la barra lateral para comenzar")

    else:

        #--- Reporte Data Drift ---
        if tipo_reporte=="DataDrift":
            with open("reports/data_drift/data_drift_report.html", 'r', encoding='utf-8') as f:
                html_data_drift = f.read()
                st.components.v1.html(html_data_drift, height=2000, scrolling=True)

        #--- Reporte Data Quality ---
        elif tipo_reporte=="DataQuality(demo)":
            with open("reports/data_quality/data_quality_report.html", 'r', encoding="utf-8") as f:
                html_data_quality = f.read()
                st.components.v1.html(html_data_quality, height=2000, scrolling=True)

        #--- Reporte Model Performance ---
        elif tipo_reporte=="ModelPerformance(demo)":
            with open("reports/model_performance/model_perform_report.html", 'r', encoding="utf-8") as  f:
                html_model_perf = f.read()
                st.components.v1.html(html_model_perf, height=2000, scrolling=True)

#======================
#Vista - Dashboards
#======================
if vista=="Dashboard":

    st.header("Dashboard")

    #Si no se ha cargado dataset mostrar mensaje
    if upload_file_csv is None:
            #entrega un mensaje en pantalla
            st.info("Carga dataset en formato CSV desde la barra lateral para comenzar")

    with st.container():

        col1 , col2 = st.columns(2)

        #Badges - estado del modelo
        #placeholder = st.empty()
        #    st.badge("Activo", color="green")
        #    st.badge("En prueba", color="yellow")
        #    st.badge("Detenido", color="red")


        with col1:
            current_model = st.selectbox(
                "Modelo actual",
                ("Modelo RL","Modelo API"),
                index=None,
                placeholder="Seleccione modelo"
            )

        with col2:

            if current_model=="Modelo RL":
                st.write("Estado: ")

            if current_model=="Modelo API":
                st.write("Estado: ")


        st.divider()

        tab1, tab2, tab3 = st.tabs(["Data Drift", "Data Quality", "Model Performance"])

        #-----------------------------
        # Pagina 1 - Data drift
        #-----------------------------
        with tab1:
            data = st.session_state.get("drift_data")

            if data is not None:
                vista_drift.render(data, dataframe_upload) #Cargamos vista de data drift

        #-----------------------------
        # Pagina 2 - Data quality
        #-----------------------------
        with tab2:
            data = st.session_state.get("quality_data")

            if data is not None:
                vista_drift.render(data, dataframe_upload) #Cargamos vista de data drift

        #-----------------------------
        # Pagina 3 - Model Performance
        #-----------------------------
        with tab3:
            data = st.session_state.get("model_data")

            if data is not None:
                vista_drift.render(data, dataframe_upload) #Cargamos vista de data drift


        