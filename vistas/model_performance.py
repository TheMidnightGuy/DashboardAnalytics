import streamlit as st 
import pandas as pd
import joblib 
import seaborn as sns
import matplotlib.pyplot as plt
import sklearn
from sklearn.metrics import confusion_matrix

def render(data: dict, dataframe_upload: pd.DataFrame | None):

    resumen     = data["resumen"]
    #features    = data["features"]
    #target      = data["target"]

    # ── Nombre del archivo cargado ──────────────────────
    st.caption(
        f"📄 Reporte cargado: "
        f"`{st.session_state.get('json_nombre', '—')}`"
    )
    st.divider()

    # ══════════════════════════════════════════════════════
    # ALERTAS
    # ══════════════════════════════════════════════════════
    st.write(
        "**Alertas y resumen ejecutivo**"
        )

    # ══════════════════════════════════════════════════════
    # SELECTBOX
    # ══════════════════════════════════════════════════════
    st.write(
        "**Columnas de predicción**"
    )

    col1, col2 = st.columns(2)

    with col1:
        df_features = st.selectbox(
            "Features",
            ("Hola", "Mundo"),
            index=None,
            placeholder="Seleccionar features"
        )

    with col2:
        df_target = st.selectbox(
            "Target",
            ("Hola", "Mundo"),
            index=None,
            placeholder="Seleccionar target"
        )

    # ══════════════════════════════════════════════════════
    # KPIs
    # ══════════════════════════════════════════════════════
    st.write("**KPIs**")

    #Current
    st.caption("Current:")

    col3, col4, col5, col6 = st.columns(4)

    with col3:
        st.metric(
            label="Accuracy",
            value="",
            border=True
        )
    with col4:
        st.metric(
            label="Precision",
            value="",
            border=True
        )
    with col5:
        st.metric(
            label="Recall",
            value="",
            border=True
        )
    with col6:
        st.metric(
            label="F1",
            value="",
            border=True
        )

    #Reference
    st.caption("Reference:")


    col7, col8, col9, col0 = st.columns(4)

    with col7:
        st.metric(
            label="Accuracy",
            value="",
            border=True
        )
    with col8:
        st.metric(
            label="Precision",
            value="",
            border=True
        )
    with col9:
        st.metric(
            label="Recall",
            value="",
            border=True
        )
    with col0:
        st.metric(
            label="F1",
            value="",
            border=True
        )

    # ══════════════════════════════════════════════════════
    # GRÁFICOS
    # ══════════════════════════════════════════════════════
    #
    st.write("**Matriz de confusión**")

    matrix1, matrix2 = st.columns(2)

    with matrix1:
        st.caption("reference")

    with matrix2:
        st.caption("current")

    #
    st.write("**Gráfico de lineas**")

    st.line_chart(
        x="a",
        y="b",
        color=["#FF0000", "#0000FF"],
    )

    #
    st.write("**Curva ROC**")


    # ══════════════════════════════════════════════════════
    # DATASET CARGADO
    # ✅ verificar None primero, luego mostrar
    # ══════════════════════════════════════════════════════
    st.write("**Dataset cargado**")

    if dataframe_upload is None:
        st.warning("Dataset CSV no cargado aún — usa el uploader de la barra lateral.")
    else:
        st.dataframe(dataframe_upload, use_container_width=True)