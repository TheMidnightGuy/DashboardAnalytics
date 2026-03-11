import streamlit as st
import pandas as pd
import time
import json
# Importaciones de terceros (Evidently, joblib, etc.)
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
# Debe ser la primera instrucción de Streamlit
st.set_page_config(
    page_title="ML Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- 2. FUNCIONES DE UTILIDAD (Caché y Lógica) ---
@st.cache_data
def cargar_datos(ruta):
    # Usar cache para no recargar CSVs pesados en cada clic
    return pd.read_csv(ruta)

def generar_reporte_evidently(ref_data, curr_data):
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref_data, current_data=curr_data)
    report.save_html("temp_report.html")
    return "temp_report.html"

# --- 3. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🛠 Configuración")
    vista = st.selectbox("Seleccionar Vista", ["Home", "Reportes", "Predicciones"])
    
    # Lógica dinámica que ya vimos
    if vista == "Reportes":
        proyecto = st.selectbox("Proyecto", ["Ventas", "Churn"])
        btn_actualizar = st.button("🔄 Actualizar Reporte")
    else:
        proyecto = None

# --- 4. CUERPO PRINCIPAL (MAIN) ---
st.header(f"Proyecto: {proyecto if proyecto else 'General'}")
st.divider()

if vista == "Home":
    st.write("Bienvenido al sistema de monitoreo.")
    # Métricas clave rápidas
    col1, col2 = st.columns(2)
    col1.metric("Modelos Activos", "4")
    col2.metric("Alertas Drift", "1", delta="-1")

elif vista == "Reportes":
    if proyecto:
        # Aquí va tu lógica de st.html o components.html
        st.info(f"Mostrando análisis de {proyecto}")
        # ... (Lógica para leer el HTML)

elif vista == "Predicciones":
    st.subheader("Simulador de API POST")
    # ... (Tu lógica de JSON/Modelo)

# --- 5. FOOTER / CRÉDITOS (Opcional) ---
st.sidebar.markdown("---")
st.sidebar.caption("v1.0.0 | Desarrollado con ❤️ y Streamlit")