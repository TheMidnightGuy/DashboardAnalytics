

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render(data: dict, dataframe_upload: pd.DataFrame | None):

    resumen    = data["resumen"]
    por_clase  = data["por_clase"]
    tests      = data["tests"]

    # ── Nombre del archivo cargado ──────────────────────
    st.caption(
        f"📄 Reporte cargado: "
        f"`{st.session_state.get('model_nombre', '—')}`"
    )
    st.divider()

    # ══════════════════════════════════════════════════════
    # ALERTAS
    # ══════════════════════════════════════════════════════
    st.write("**Alertas y resumen ejecutivo**")

    accuracy = resumen.get("accuracy", 0)
    f1       = resumen.get("f1", 0)

    if accuracy < 0.7:
        st.error(
            f"Accuracy baja — {accuracy:.2%}",
            icon="🟥"
        )
    elif accuracy < 0.85:
        st.warning(
            f"Accuracy moderada — {accuracy:.2%}",
            icon="⚠️"
        )
    else:
        st.success(f"Accuracy saludable — {accuracy:.2%}")

    if f1 < 0.5:
        st.warning(
            f"F1 Score bajo — {f1:.2%}. Revisar balance precision/recall.",
            icon="⚠️"
        )

    if tests:
        with st.expander(f"🔴 {len(tests)} tests fallidos — ver detalle"):
            for t in tests:
                icon = "🔴" if t["critico"] else "🟡"
                st.warning(
                    f"**{t['nombre']}** — {t['descripcion']}",
                    icon=icon
                )

    st.divider()

    # ══════════════════════════════════════════════════════
    # KPIs — métricas principales
    # ══════════════════════════════════════════════════════
    st.write("**KPIs**")

    st.caption("Métricas principales:")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Accuracy",
            value=f"{resumen.get('accuracy', 0):.2%}",
            border=True
        )
    with col2:
        st.metric(
            label="Precision",
            value=f"{resumen.get('precision', 0):.2%}",
            border=True
        )
    with col3:
        st.metric(
            label="Recall",
            value=f"{resumen.get('recall', 0):.2%}",
            border=True
        )
    with col4:
        st.metric(
            label="F1 Score",
            value=f"{resumen.get('f1', 0):.2%}",
            border=True
        )

    # KPIs — tasas secundarias
    st.caption("Tasas de clasificación:")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric(
            label="TPR (Sensibilidad)",
            value=f"{resumen.get('tpr', 0):.2%}",
            border=True
        )
    with col6:
        st.metric(
            label="TNR (Especificidad)",
            value=f"{resumen.get('tnr', 0):.2%}",
            border=True
        )
    with col7:
        st.metric(
            label="FPR",
            value=f"{resumen.get('fpr', 0):.2%}",
            border=True
        )
    with col8:
        st.metric(
            label="FNR",
            value=f"{resumen.get('fnr', 0):.2%}",
            border=True
        )

    st.divider()

    # ══════════════════════════════════════════════════════
    # MÉTRICAS POR CLASE — gráfico + tabla
    # ══════════════════════════════════════════════════════
    st.write("**Métricas por clase**")

    if por_clase:
        col_izq, col_der = st.columns(2)

        # ── Tabla izquierda ─────────────────────────────
        with col_izq:
            # Obtener clases de cualquier métrica disponible
            clases = sorted(
                next(iter(por_clase.values())).keys()
            ) if por_clase else []

            filas_clase = []
            for clase in clases:
                fila = {"Clase": clase}
                for metrica, valores in por_clase.items():
                    fila[metrica.capitalize()] = valores.get(clase, 0)
                filas_clase.append(fila)

            df_clases = pd.DataFrame(filas_clase)
            st.dataframe(
                df_clases,
                use_container_width=True,
                hide_index=True,
                column_config={
                    col: st.column_config.ProgressColumn(
                        col,
                        min_value=0,
                        max_value=1,
                        format="%.4f",
                    )
                    for col in df_clases.columns if col != "Clase"
                }
            )

        # ── Gráfico derecha ─────────────────────────────
        with col_der:
            filas_grafico = []
            for metrica, valores in por_clase.items():
                for clase, val in valores.items():
                    filas_grafico.append({
                        "Clase":   str(clase),
                        "Métrica": metrica.capitalize(),
                        "Valor":   val,
                    })

            df_grafico = pd.DataFrame(filas_grafico)

            fig = px.bar(
                df_grafico,
                x="Métrica",
                y="Valor",
                color="Clase",
                barmode="group",
                color_discrete_sequence=["#3B8BD4", "#E24B4A"],
                title="Precision / Recall / F1 por clase",
            )
            fig.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=40, b=20),
                yaxis_tickformat=".0%",
                yaxis_range=[0, 1],
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de métricas por clase disponibles.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # RESUMEN GENERAL — gráfico radar / barras horizontal
    # ══════════════════════════════════════════════════════
    st.write("**Resumen de métricas globales**")

    metricas_nombres = ["Accuracy", "Precision", "Recall", "F1", "TPR", "TNR"]
    metricas_claves  = ["accuracy", "precision", "recall", "f1", "tpr", "tnr"]
    metricas_valores = [resumen.get(k, 0) for k in metricas_claves]

    df_resumen = pd.DataFrame({
        "Métrica": metricas_nombres,
        "Valor":   metricas_valores,
    }).sort_values("Valor", ascending=True)

    fig_resumen = px.bar(
        df_resumen,
        x="Valor",
        y="Métrica",
        orientation="h",
        color_discrete_sequence=["#3B8BD4"],
        title="Métricas globales del modelo",
    )
    fig_resumen.update_layout(
        height=300,
        margin=dict(l=0, r=10, t=40, b=20),
        xaxis_tickformat=".0%",
        xaxis_range=[0, 1],
    )
    st.plotly_chart(fig_resumen, use_container_width=True)

    st.divider()

    # ══════════════════════════════════════════════════════
    # DATASET CARGADO
    # ✅ verificar None primero, luego mostrar
    # ══════════════════════════════════════════════════════
    st.write("**Dataset cargado**")

    if dataframe_upload is None:
        st.warning("Dataset CSV no cargado aún — usa el uploader de la barra lateral.")
    else:
        st.dataframe(dataframe_upload, use_container_width=True)
