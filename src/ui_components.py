import streamlit as st

def get_driver_metadata(session, driver_code: str):
    # Simulação da obtenção de dados
    drv = session.get_driver(driver_code)
    full_name = getattr(drv, "FullName", driver_code) or driver_code
    team_name = getattr(drv, "TeamName", "")
    # FastF1 retorna hex sem o '#'
    team_color = f"#{getattr(drv, 'TeamColor', '444444')}"
    return full_name, team_name, team_color

def render_driver_header(session, side_label: str, driver_code: str):
    full_name, team_name, team_color = get_driver_metadata(session, driver_code)

    # Isso evita o preto total e cria um "glow" da equipe no card
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, {team_color}22 0%, #1e1e23 100%);
        border-left: 12px solid {team_color};
        padding: 20px 25px;
        border-radius: 4px 15px 15px 4px;
        margin: 10px 0;
        border-top: 1px solid {team_color}44;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    ">
        <p style="
            color: {team_color};
            font-size: 11px;
            margin: 0;
            text-transform: uppercase;
            font-weight: 800;
            letter-spacing: 2px;
        ">{side_label}</p>
        <h2 style="
            color: white;
            margin: 5px 0;
            font-size: 26px;
            font-weight: 900;
            line-height: 1;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        ">{full_name.upper()}</h2>
        <p style="
            color: #DDDDDD;
            margin: 0;
            font-size: 13px;
            font-weight: 400;
            letter-spacing: 0.5px;
        ">{team_name.upper()}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)