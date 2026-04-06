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
import hashlib
import os

#importamos modulos y vistas
from core.parser import parsear_drift, parsear_quality, parsear_model

import vistas.data_drift as vista_drift
import vistas.data_quality as vista_quality
import vistas.model_performance as vista_model

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
# Control de cache
#======================
#Para evitar cargar la aplicación completa cada vez que se inicia la aplicación integraremos control de cache con 'st.cache_data'
#El manejo de estas es mediante funciones Python

@st.cache_data
def cargar_csv(file_content: bytes) -> pd.DataFrame:
    """Cachea la lectura del CSV. Solo se re-ejecuta si el contenido del archivo cambia."""
    from io import BytesIO
    return pd.read_csv(BytesIO(file_content))

@st.cache_data
def cargar_y_parsear_drift(json_path: str, _file_hash: str) -> dict:
    """Cachea el parseo del JSON. _file_hash fuerza invalidación cuando cambia el archivo."""
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return parsear_drift(raw)

@st.cache_data
def cargar_y_parsear_quality(json_path: str, _file_hash: str) -> dict:
    """Cachea el parseo del JSON de quality. _file_hash fuerza invalidación cuando cambia el archivo."""
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return parsear_quality(raw)

@st.cache_data
def cargar_y_parsear_model(json_path: str, _file_hash: str) -> dict:
    """Cachea el parseo del JSON de model performance. _file_hash fuerza invalidación cuando cambia el archivo."""
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return parsear_model(raw)




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
            ("DataDrift","DataQuality","ModelPerformance(demo)"),
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

    dataframe_upload = None

    #Cada vez que se ejecuta app.py el boton de carga de archivos debe estar vacio.
    upload_file_csv = None

    upload_file_csv= st.file_uploader(
        label="**Cargar dataset**",
        type="csv",
        max_upload_size=500,
        accept_multiple_files=False
    )

    #Disclaimer
    st.caption("Nota: El tiempo de procesamiento del archivo CSV depende del equipo donde se ejecute y el volumen de datos.")

    #Dataset hacia notebook evidently
    if upload_file_csv is not None:
        # Generar hash del archivo para detectar si cambió
        file_bytes = upload_file_csv.getvalue()
        file_hash = hashlib.md5(file_bytes).hexdigest()

        # Leer CSV cacheado (no se re-lee si es el mismo archivo)
        dataframe_upload = cargar_csv(file_bytes)

        # Solo ejecutar el pipeline si el archivo es nuevo
        if st.session_state.get("last_file_hash") != file_hash:
            dataframe_upload.to_csv("data/uploaded.csv", index=False)

            # Ejecutamos diagnostico.py
            # .Popen -> entrega output durante ejecución.
            proceso = subprocess.Popen(
                [sys.executable, "src/diagnostico.py"],
                text=True,
                stdout= subprocess.PIPE,
                stderr= subprocess.STDOUT
            )

            #Ya configurado el output lo mostramos en la terminal durante ejecución de streamlit.
            for linea in proceso.stdout:
                print(linea, end="")

            #Esperamos a que el proceso termine para obtener returncode.
            proceso.wait()

            #Una vez termino el flujo del notebook:
            #   lee el json generado para posteriormente parser.py lo procese
            if proceso.returncode == 0:
                drift_data = cargar_y_parsear_drift(
                    "data/snapshots/data_drift_report.json", file_hash
                )
                quality_data = cargar_y_parsear_quality(
                    "data/snapshots/data_quality_report.json", file_hash
                )
                model_data = None
                model_perf_path = "data/snapshots/model_performance_report.json"
                if os.path.exists(model_perf_path):
                    model_data = cargar_y_parsear_model(model_perf_path, file_hash)

                #Usamos 'st.session_state' para persistir variables entre ejecuciones de streamlit.
                st.session_state["drift_data"] =        drift_data
                st.session_state["drift_nombre"] =      "data_drift_report.json"
                st.session_state["quality_data"] =      quality_data
                st.session_state["quality_nombre"] = "  data_quality_report.json"
                st.session_state["last_file_hash"] =    file_hash
                st.session_state["model_data"] =        model_data
                st.session_state["model_nombre"] =      "model_performance.json"

                #Alerta para validar que se ha cargado correctamente el archivo csv.
                st.success("Archivo CSV cargado correctamente!", icon="🟢")

            #Logs para captar error en caso de que archivo no cargue correctamente.
            else:
                st.error(f"Error en procesamiento (codigo {proceso.returncode})")
        else:
            # El archivo ya fue procesado, usamos datos del cache
            st.success("Dataset ya procesado (desde cache)", icon="🟢")
    
    else:
        #Si se quita el csv cargado eliminamos la data que persiste. (usamos .pop)
        #(drift_data / drift_nombre / quality_data / quality_nombre / last_file_hash)
        st.warning("Archivo 'uploaded.csv' se encuentra sin contenido")
        st.session_state.pop("drift_data", None)
        st.session_state.pop("drift_nombre", None)
        st.session_state.pop("quality_data", None)
        st.session_state.pop("quality_nombre", None)
        st.session_state.pop("last_file_hash", None)
        st.session_state.pop("model_data", None)
        st.session_state.pop("model_nombre", None)

    #--- Sección Exportar ---
    #st.write("---------------")

    #Subheader exporta (según vista)
    if vista=="Dashboard":    
        st.subheader("Exportar Dashboard")
    elif vista=="Reporte":
        st.subheader("Exportar Reporte")

    #Formato a exportar

    formato_exp = st.selectbox(
        "Formato",
        ("HTML","PDF"),
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
    #if vista=="Dashboard":

    #




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

            #Datasets cargados
            st.header("Datasets evidently")

            df_ref = dataframe_upload
            df_act = pd.read_csv("data/modified.csv")

            #Dataset Referencia
            st.subheader("Dataset de referencia")
            st.dataframe(df_ref)

            #Dataset Actual
            st.subheader("Dataset actual")
            st.dataframe(df_act)

        #--- Reporte Data Quality ---
        elif tipo_reporte=="DataQuality":
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
                vista_quality.render(data, dataframe_upload) #Cargamos vista de data quality

        #-----------------------------
        # Pagina 3 - Model Performance
        #-----------------------------
        with tab3:
            data = st.session_state.get("model_data")

            if data is not None:
                vista_model.render(data, dataframe_upload) #Cargamos vista de Model Performance
            elif upload_file_csv is not None:
                st.info("No se generó reporte de Model Performance — el dataset no tiene columna target binaria.")


        