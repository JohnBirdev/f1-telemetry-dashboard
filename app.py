import streamlit as st
from src.processing import prepare_lap_data, get_fastest_lap_telemetry, get_fastest_lap_summary
from src.data_loader import load_session, get_schedules
from src.plots import (
    plot_animated_circuit,
    plot_all_race_laps_overview,
    render_driver_table,
    plot_animated_circuit_comparison,
)
from src.simulation import interpolate_telemetry
from src.ui_components import render_driver_header

st.set_page_config(
    page_title="F1 Telemetry Dashboard",
    page_icon="🏎️",
    layout="wide",
)

# ==============================
# Sidebar Controls
# ==============================

year = st.sidebar.selectbox("Escolha o ano: ", options=range(2021, 2027))

# UX: mais alto
animation_performance = st.sidebar.slider(
    "Velocidade da animação",
    min_value=1,
    max_value=10,
    value=5,
    step=1,
    help=(
        "A animação fica mais rápida quando usamos menos frames/pontos."
    ),
)

_MIN_STEPS = 200
_MAX_STEPS = 1200
animation_steps = int(
    _MAX_STEPS - (animation_performance - 1) * (_MAX_STEPS - _MIN_STEPS) / 9
)

@st.cache_data(show_spinner=False)
def load_schedule(year: int):
    return get_schedules(year)


schedule = load_schedule(year)

selected_event = st.sidebar.selectbox(
    "Escolha a corrida",
    schedule['EventName']
)

round_number = schedule[
    schedule['EventName'] == selected_event
]['RoundNumber'].values[0]

# ==============================
# Cached Loaders
# ==============================

@st.cache_resource(show_spinner=True)
def get_session(year: int, round_number: int):
    return load_session(year, round_number, telemetry=True, laps=True, weather=False)


@st.cache_data(show_spinner=True)
def load_laps(year, round_number):
    session = get_session(year, round_number)
    return prepare_lap_data(session)


@st.cache_data(show_spinner=True)
def load_telemetry(year, round_number, driver):
    session = get_session(year, round_number)
    return get_fastest_lap_telemetry(session, driver, minimal=True)


@st.cache_data(show_spinner=True)
def load_fastest_summary(year, round_number, driver: str):
    session = get_session(year, round_number)
    return get_fastest_lap_summary(session, driver)


laps = load_laps(year, round_number)

# ==============================
# Tabs
# ==============================

tab1, tab2 = st.tabs(["Análise de Voltas", "Comparação de Pilotos"])

# ============================================
# 📊 TAB 1 — ANÁLISE DE VOLTAS
# ============================================

with tab1:

    st.markdown(
        "<h1 style='text-align:center;'>F1 Telemetry Dashboard</h1>",
        unsafe_allow_html=True,
    )

    drivers = laps['Driver'].unique()
    driver = st.selectbox("Escolha o piloto", drivers)

    # -----------------------------
    # Gráfico todas as voltas corrida
    # -----------------------------
    st.subheader("Visão Geral da Corrida")
    fig_all = plot_all_race_laps_overview(laps)
    st.plotly_chart(fig_all, use_container_width=True)

    # -----------------------------
    # Gráfico piloto selecionado
    # -----------------------------
    st.subheader(f"Tabela de Voltas: {driver}")
    render_driver_table(laps, driver)
    

    # -----------------------------
    # Melhor volta piloto
    # -----------------------------
    best_lap_seconds = laps[
        laps['Driver'] == driver
    ]['LapTimeSeconds'].min()

    minutes = int(best_lap_seconds // 60)
    seconds = best_lap_seconds % 60
    formatted_time = f"{minutes}:{seconds:06.3f}"

    st.metric("Melhor volta do piloto:", formatted_time)

    st.divider()

    # -----------------------------
    # Simulação
    # -----------------------------
    st.subheader("Simulação da Melhor Volta do Piloto")

    try:
        telemetry = load_telemetry(year, round_number, driver)
        x, y, t, sectors = interpolate_telemetry(telemetry, steps=animation_steps)
        fig_circuit = plot_animated_circuit(x, y, sectors, driver)
        st.plotly_chart(fig_circuit, use_container_width=True)

    except Exception as e:
        st.error(f"Erro real: {e}")

# ============================================
# ⚔️ TAB 2 — COMPARAÇÃO
# ============================================

with tab2:

    st.markdown(
        "<h1 style='text-align:center;'>Comparação de Pilotos</h1>",
        unsafe_allow_html=True,
    )

    drivers = laps['Driver'].unique()

    col1, col2 = st.columns(2)

    with col1:
        driver1 = st.selectbox("Piloto 1", drivers, key="d1")

    with col2:
        driver2 = st.selectbox("Piloto 2", drivers, key="d2")

    if driver1 != driver2:
        session = get_session(year, round_number)
        # Deixar os cards mais próximos, reduzindo o espaço central
        header_left, header_center, header_right = st.columns([4, 0.4, 4])

        with header_left:
            render_driver_header(session, "Piloto 1", driver1)

        with header_center:
            st.markdown(
        """
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            margin-top: 45px;
        ">
            <div style="
                background: #1e1e23;
                color: #888;
                font-size: 20px;
                font-weight: 900;
                padding: 10px;
                border: 3px solid #333;
                border-radius: 50%;
                width: 45px;
                height: 45px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 0 15px rgba(0,0,0,0.5);
            ">
                VS
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

        with header_right:
            render_driver_header(session, "Piloto 2", driver2)

        def _fmt_time(seconds: float | None) -> str:
            if seconds is None:
                return "—"
            mins = int(seconds // 60)
            secs = seconds % 60
            return f"{mins}:{secs:06.3f}"

        def _fmt_speed(kmh: float | None) -> str:
            if kmh is None:
                return "—"
            return f"{kmh:.0f} km/h"

        s1 = load_fastest_summary(year, round_number, driver1)
        s2 = load_fastest_summary(year, round_number, driver2)

        # Linha de métricas alinhada aos cards, dentro de "cards" de stats
        m_left, m_right = st.columns([4, 4])

        with m_left:
            left_html = f"""
        <div style="
        margin-top:10px;
        padding:16px 18px;
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border-radius:10px;
        border:1px solid rgba(255,255,255,0.08);
        font-size:13px;
        opacity:0.95;">

        <div style="font-weight:800; text-align:center; margin-bottom:12px; font-size:15px;">
        {driver1}
        </div>

        <div style="
        display:grid;
        grid-template-columns: 1fr 1fr;
        text-align:center;
        margin-bottom:8px;
        font-weight:600;
        opacity:0.8;
        ">
        <div>Lap Time</div>
        <div>Top Speed</div>
        </div>

        <div style="
        display:grid;
        grid-template-columns: 1fr 1fr;
        text-align:center;
        font-size:22px;
        font-weight:800;
        margin-bottom:14px;
        ">
        <div>{_fmt_time(s1.get("lap_time_s"))}</div>
        <div>{_fmt_speed(s1.get("top_speed_kmh"))}</div>
        </div>

        <div style="text-align:center; margin-top:4px;">
        <div style="font-weight:700;">S1</div>
        <div style="font-size:18px; margin-bottom:6px;">{_fmt_time(s1.get("s1_s"))}</div>

        <div style="font-weight:700;">S2</div>
        <div style="font-size:18px; margin-bottom:6px;">{_fmt_time(s1.get("s2_s"))}</div>

        <div style="font-weight:700;">S3</div>
        <div style="font-size:18px;">{_fmt_time(s1.get("s3_s"))}</div>
        </div>

        </div>
        """
            st.markdown(left_html, unsafe_allow_html=True)

        with m_right:
            right_html = f"""
        <div style="
        margin-top:10px;
        padding:16px 18px;
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        border-radius:10px;
        border:1px solid rgba(255,255,255,0.08);
        font-size:13px;
        opacity:0.95;">

        <div style="font-weight:800; text-align:center; margin-bottom:12px; font-size:15px;">
        {driver2}
        </div>

        <div style="
        display:grid;
        grid-template-columns: 1fr 1fr;
        text-align:center;
        margin-bottom:8px;
        font-weight:600;
        opacity:0.8;
        ">
        <div>Lap Time</div>
        <div>Top Speed</div>
        </div>

        <div style="
        display:grid;
        grid-template-columns: 1fr 1fr;
        text-align:center;
        font-size:22px;
        font-weight:800;
        margin-bottom:14px;
        ">
        <div>{_fmt_time(s2.get("lap_time_s"))}</div>
        <div>{_fmt_speed(s2.get("top_speed_kmh"))}</div>
        </div>

        <div style="text-align:center; margin-top:4px;">
        <div style="font-weight:700;">S1</div>
        <div style="font-size:18px; margin-bottom:6px;">{_fmt_time(s2.get("s1_s"))}</div>

        <div style="font-weight:700;">S2</div>
        <div style="font-size:18px; margin-bottom:6px;">{_fmt_time(s2.get("s2_s"))}</div>

        <div style="font-weight:700;">S3</div>
        <div style="font-size:18px;">{_fmt_time(s2.get("s3_s"))}</div>
        </div>

        </div>
        """
            st.markdown(right_html, unsafe_allow_html=True)

            



        # Bloco de delta embaixo dos dois cards de stats
        lap_delta = None
        if s1.get("lap_time_s") is not None and s2.get("lap_time_s") is not None:
            lap_delta = s2["lap_time_s"] - s1["lap_time_s"]

        s1_delta = None
        if s1.get("s1_s") is not None and s2.get("s1_s") is not None:
            s1_delta = s2["s1_s"] - s1["s1_s"]
        s2_delta = None
        if s1.get("s2_s") is not None and s2.get("s2_s") is not None:
            s2_delta = s2["s2_s"] - s1["s2_s"]
        s3_delta = None
        if s1.get("s3_s") is not None and s2.get("s3_s") is not None:
            s3_delta = s2["s3_s"] - s1["s3_s"]

        _, delta_col, _ = st.columns([3, 2, 3])
        delta_html = f"""
        <div style="
            margin-top:10px;
            padding:12px 14px;
            background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
            border-radius:10px;
            border:1px solid rgba(255,255,255,0.08);
            text-align:center;
            font-size:13px;
            opacity:0.9;
        ">
            <div style="font-weight:800; margin-bottom:6px;">DELTA (P2 − P1)</div>
            <div><b>Lap</b>: {('—' if lap_delta is None else f'{lap_delta:+.3f}s')}</div>
            <div><b>S1</b>: {('—' if s1_delta is None else f'{s1_delta:+.3f}s')}</div>
            <div><b>S2</b>: {('—' if s2_delta is None else f'{s2_delta:+.3f}s')}</div>
            <div><b>S3</b>: {('—' if s3_delta is None else f'{s3_delta:+.3f}s')}</div>
        </div>
        """
        with delta_col:
            st.markdown(delta_html, unsafe_allow_html=True)

        telemetry1 = load_telemetry(year, round_number, driver1)
        telemetry2 = load_telemetry(year, round_number, driver2)

        x1, y1, t1, sectors1 = interpolate_telemetry(telemetry1, steps=animation_steps)
        x2, y2, t2, sectors2 = interpolate_telemetry(telemetry2, steps=animation_steps)

        fig = plot_animated_circuit_comparison(
            x1, y1, t1, sectors1, driver1,
            x2, y2, t2, sectors2, driver2,
            steps=animation_steps,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Selecione dois pilotos diferentes.")

    st.caption("Data source: FastF1 API")