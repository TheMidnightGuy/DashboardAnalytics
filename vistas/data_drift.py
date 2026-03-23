

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render(data: dict, dataframe_upload: pd.DataFrame | None):

    dataset  = data["dataset"]
    columnas = data["columnas"]

    # ── Nombre del archivo cargado ──────────────────────
    st.caption(
        f"📄 Reporte cargado: "
        f"`{st.session_state.get('json_nombre', '—')}`"
    )
    st.divider()

    # ══════════════════════════════════════════════════════
    # ALERTAS — leen de data["dataset"], no hardcodeadas
    # ══════════════════════════════════════════════════════
    st.write("**Alertas y resumen ejecutivo**")

    if dataset["drift_detected"]:
        st.error(
            f"Dataset drift detectado — "
            f"{dataset['n_drifted']} de {dataset['n_total']} columnas "
            f"({dataset['drift_share']:.1%})",
            icon="🟥"
        )
    else:
        st.success("✅ Sin drift detectado a nivel de dataset")

    # Detalle por columna en expander
    cols_drift = [c for c, d in columnas.items() if d["drift_detected"]]
    if cols_drift:
        with st.expander(f"⚠️ {len(cols_drift)} columnas con drift — ver detalle"):
            for col in cols_drift:
                d = columnas[col]
                st.warning(
                    f"**{col}** — "
                    f"score: `{d['drift_score']}` · "
                    f"test: {d['stattest']} · "
                    f"umbral: {d['threshold']}",
                    icon="⚠️"
                )

    st.divider()

    # ══════════════════════════════════════════════════════
    # KPIs — leen de data["dataset"]
    # delta_color válido: "normal", "inverse", "off"
    # ══════════════════════════════════════════════════════
    st.write("**KPIs**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Dataset drift",
            value="Detectado" if dataset["drift_detected"] else "OK",
            border=True
        )
    with col2:
        st.metric(
            label="Drift share",
            value=f"{dataset['drift_share']:.1%}",
            border=True
        )
    with col3:
        st.metric(
            label="Columnas con drift",
            value=f"{dataset['n_drifted']} / {dataset['n_total']}",
            border=True
        )
    with col4:
        st.metric(
            label="Columnas sin drift",
            value=f"{dataset['n_total'] - dataset['n_drifted']}",
            border=True
        )

    st.divider()

    # ══════════════════════════════════════════════════════
    # ANÁLISIS POR COLUMNA — tabla + barras
    # ══════════════════════════════════════════════════════
    st.write("**Análisis por columna**")

    col_izq, col_der = st.columns(2)

    # ── Tabla izquierda ─────────────────────────────────
    with col_izq:
        filas = [
            {
                "Columna": col,
                "Test":    d["stattest"],
                "Score":   d["drift_score"],
                "Umbral":  d["threshold"],
                "Estado":  "Drift" if d["drift_detected"] else "Normal",
            }
            for col, d in columnas.items()
        ]
        df_tabla = (
            pd.DataFrame(filas)
            .sort_values("Score", ascending=False)
        )
        st.dataframe(
            df_tabla,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Score",
                    min_value=0,
                    max_value=1,
                    format="%.4f",
                ),
            }
        )

    # ── Barras derecha ───────────────────────────────────
    with col_der:
        # .sort_values() dentro del paréntesis
        df_barras = (
            pd.DataFrame([
                {
                    "columna":        col,
                    "drift_score":    d["drift_score"],
                    "drift_detected": d["drift_detected"],
                }
                for col, d in columnas.items()
            ])
            .sort_values("drift_score", ascending=True)
        )

        fig = px.bar(
            df_barras,
            x="drift_score",
            y="columna",
            orientation="h",
            color="drift_detected",
            color_discrete_map={True: "#E24B4A", False: "#3B8BD4"},
            labels={
                "drift_score":    "Drift score",
                "columna":        "",
                "drift_detected": "Drift"
            },
            title="Drift score por columna",
        )
        fig.add_vline(
            x=0.1,
            line_dash="dot",
            line_color="orange",
            annotation_text="umbral 0.1",
            annotation_position="top right"
        )
        fig.update_layout(
            height=max(300, len(columnas) * 28),
            margin=dict(l=0, r=10, t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ══════════════════════════════════════════════════════
    # DISTRIBUCIÓN POR COLUMNA
    # ══════════════════════════════════════════════════════
    st.write("**Distribución por columna**")

    col_sel = st.selectbox(
        "Selecciona columna",
        options=list(columnas.keys()),
        index=0
    )

    d_sel = columnas[col_sel]
    ref   = d_sel.get("reference_distr", {})
    curr  = d_sel.get("current_distr",   {})

    if ref and curr:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=ref.get("x", []),
            y=ref.get("y", []),
            name="Referencia",
            opacity=0.6,
            marker_color="#3B8BD4",
        ))
        fig2.add_trace(go.Bar(
            x=curr.get("x", []),
            y=curr.get("y", []),
            name="Actual",
            opacity=0.6,
            marker_color="#E24B4A",
        ))
        fig2.update_layout(
            barmode="overlay",
            title=f"Distribución — {col_sel}",
            xaxis_title=col_sel,
            yaxis_title="Frecuencia",
            legend=dict(orientation="h", y=1.1),
            margin=dict(l=0, r=0, t=50, b=20),
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info(
            "Distribución no disponible — el preset DataDrift "
            "no incluye histogramas en esta versión de Evidently. "
            "Agrega ColumnSummaryMetric en el notebook para habilitarla."
        )

    # Mini métricas bajo el selector
    m1, m2, m3 = st.columns(3)
    m1.metric("Test usado",  d_sel["stattest"])
    m2.metric("Drift score", d_sel["drift_score"])
    m3.metric("Umbral",      d_sel["threshold"])

    st.divider()

    # ══════════════════════════════════════════════════════
    # ESTADÍSTICOS COMPLETOS — colapsado
    # ══════════════════════════════════════════════════════
    with st.expander("Ver detalle estadístico completo"):
        df_stats = (
            pd.DataFrame([
                {
                    "Columna":         col,
                    "Test":            d["stattest"],
                    "Score":           d["drift_score"],
                    "Umbral":          d["threshold"],
                    "Drift detectado": d["drift_detected"],
                }
                for col, d in columnas.items()
            ])
            .sort_values("Score", ascending=False)
        )
        st.dataframe(
            df_stats,
            use_container_width=True,
            hide_index=True
        )

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