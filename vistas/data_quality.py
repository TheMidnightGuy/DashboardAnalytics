

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render(data: dict, dataframe_upload: pd.DataFrame | None):

    resumen     = data["resumen"]
    nulos       = data["nulos"]
    numericas   = data["numericas"]
    categoricas = data["categoricas"]
    tests       = data["tests"]

    # ── Nombre del archivo cargado ──────────────────────
    st.caption(
        f"📄 Reporte cargado: "
        f"`{st.session_state.get('json_nombre', '—')}`"
    )
    st.divider()

    # ══════════════════════════════════════════════════════
    # ALERTAS
    # ══════════════════════════════════════════════════════
    st.write("**Alertas y resumen ejecutivo**")

    nulos_share = resumen.get("nulos_share", 0)
    filas_dup   = resumen.get("filas_duplicadas", 0)
    cols_vacias = resumen.get("cols_vacias", 0)

    if nulos_share > 0.1:
        st.error(
            f"Alto porcentaje de valores nulos — {nulos_share:.1%} del dataset",
            icon="🟥"
        )
    elif nulos_share > 0:
        st.warning(
            f"Valores nulos detectados — {nulos_share:.1%} del dataset",
            icon="⚠️"
        )
    else:
        st.success("Sin valores nulos en el dataset")

    if filas_dup > 0:
        st.warning(
            f"{filas_dup} filas duplicadas detectadas",
            icon="⚠️"
        )

    if cols_vacias > 0:
        st.error(
            f"{cols_vacias} columnas completamente vacias",
            icon="🟥"
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
    # KPIs
    # ══════════════════════════════════════════════════════
    st.write("**KPIs**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Filas",
            value=f"{resumen.get('n_filas', 0):,}",
            border=True
        )
    with col2:
        st.metric(
            label="Columnas",
            value=f"{resumen.get('n_columnas', 0)}",
            border=True
        )
    with col3:
        st.metric(
            label="Nulos totales",
            value=f"{resumen.get('nulos_total', 0):,}",
            border=True
        )
    with col4:
        st.metric(
            label="Filas duplicadas",
            value=f"{filas_dup:,}",
            border=True
        )

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric(
            label="Numericas",
            value=f"{resumen.get('n_numericas', 0)}",
            border=True
        )
    with col6:
        st.metric(
            label="Categoricas",
            value=f"{resumen.get('n_categoricas', 0)}",
            border=True
        )
    with col7:
        st.metric(
            label="Cols. casi constantes",
            value=f"{resumen.get('cols_casi_constantes', 0)}",
            border=True
        )
    with col8:
        st.metric(
            label="Cols. vacias",
            value=f"{cols_vacias}",
            border=True
        )

    st.divider()

    # ══════════════════════════════════════════════════════
    # NULOS POR COLUMNA — tabla + barras
    # ══════════════════════════════════════════════════════
    st.write("**Valores nulos por columna**")

    if nulos:
        col_izq, col_der = st.columns(2)

        # ── Tabla izquierda ─────────────────────────────
        with col_izq:
            filas_nulos = [
                {
                    "Columna": col,
                    "Nulos":   d["count"],
                    "% Nulos": d["share"],
                }
                for col, d in nulos.items()
            ]
            df_nulos = (
                pd.DataFrame(filas_nulos)
                .sort_values("% Nulos", ascending=False)
            )
            st.dataframe(
                df_nulos,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "% Nulos": st.column_config.ProgressColumn(
                        "% Nulos",
                        min_value=0,
                        max_value=1,
                        format="%.2%",
                    ),
                }
            )

        # ── Barras derecha ──────────────────────────────
        with col_der:
            df_barras = (
                pd.DataFrame([
                    {
                        "columna":   col,
                        "nulos_pct": d["share"],
                        "tiene_nulos": d["count"] > 0,
                    }
                    for col, d in nulos.items()
                ])
                .sort_values("nulos_pct", ascending=True)
            )

            fig = px.bar(
                df_barras,
                x="nulos_pct",
                y="columna",
                orientation="h",
                color="tiene_nulos",
                color_discrete_map={True: "#E24B4A", False: "#3B8BD4"},
                labels={
                    "nulos_pct": "% Nulos",
                    "columna":   "",
                    "tiene_nulos": "Con nulos"
                },
                title="Porcentaje de nulos por columna",
            )
            fig.update_layout(
                height=max(300, len(nulos) * 28),
                margin=dict(l=0, r=10, t=40, b=20),
                xaxis_tickformat=".0%",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de nulos por columna disponibles.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # ESTADISTICOS NUMERICOS
    # ══════════════════════════════════════════════════════
    st.write("**Estadisticos — columnas numericas**")

    if numericas:
        col_sel = st.selectbox(
            "Selecciona columna numerica",
            options=list(numericas.keys()),
            index=0,
            key="quality_num_col"
        )

        stats = numericas[col_sel]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Min",  stats.get("min", "—"))
        m2.metric("Max",  stats.get("max", "—"))
        m3.metric("Mean", stats.get("mean", "—"))
        m4.metric("Std",  stats.get("std", "—"))

        m5, m6, m7 = st.columns(3)
        m5.metric("P25", stats.get("p25", "—"))
        m6.metric("P50 (mediana)", stats.get("p50", "—"))
        m7.metric("P75", stats.get("p75", "—"))

        # Tabla resumen de todas las numericas
        with st.expander("Ver tabla completa de estadisticos numericos"):
            filas_num = []
            for col, s in numericas.items():
                filas_num.append({
                    "Columna": col,
                    "Min":     s.get("min", None),
                    "P25":     s.get("p25", None),
                    "Media":   s.get("mean", None),
                    "P50":     s.get("p50", None),
                    "P75":     s.get("p75", None),
                    "Max":     s.get("max", None),
                    "Std":     s.get("std", None),
                })
            st.dataframe(
                pd.DataFrame(filas_num),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No hay columnas numericas en el dataset.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # CATEGORICAS — distribucion de valores
    # ══════════════════════════════════════════════════════
    st.write("**Distribucion — columnas categoricas**")

    if categoricas:
        col_cat = st.selectbox(
            "Selecciona columna categorica",
            options=list(categoricas.keys()),
            index=0,
            key="quality_cat_col"
        )

        cat_data = categoricas[col_cat]
        counts = cat_data.get("counts", {})

        if counts:
            df_cat = pd.DataFrame({
                "Valor": list(counts.keys()),
                "Conteo": list(counts.values()),
            }).sort_values("Conteo", ascending=False)

            fig_cat = px.bar(
                df_cat,
                x="Valor",
                y="Conteo",
                title=f"Distribucion de valores — {col_cat}",
                color_discrete_sequence=["#3B8BD4"],
            )
            fig_cat.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=40, b=20),
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info(f"Sin datos de distribucion para '{col_cat}'.")
    else:
        st.info("No hay columnas categoricas en el dataset.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # DATASET CARGADO
    # ══════════════════════════════════════════════════════
    st.write("**Dataset cargado**")

    if dataframe_upload is None:
        st.warning("Dataset CSV no cargado aun — usa el uploader de la barra lateral.")
    else:
        st.dataframe(dataframe_upload, use_container_width=True)
