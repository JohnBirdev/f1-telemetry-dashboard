import plotly.graph_objects as go
import numpy as np
import streamlit as st

DRIVER_COLORS = {
    "VER": "blue",
    "LEC": "red",
    "HAM": "cyan",
    "NOR": "orange"
}

def plot_animated_circuit(x, y, sectors, driver):

    driver_color = DRIVER_COLORS.get(driver, "white")

    #Separar traçado por setor
    sector_colors = {
        1: "purple",
        2: "green",
        3: "yellow"
    }

    traces = []

    for sector in [1, 2, 3]:
        mask = sectors == sector
        traces.append(
            go.Scatter(
                x=np.array(x)[mask],
                y=np.array(y)[mask],
                mode="lines",
                line=dict(color=sector_colors[sector], width=3),
                showlegend=False
            )
        )

    #marcador inicial com label
    marker = go.Scatter(
        x=[x[0]],
        y=[y[0]],
        mode="markers+text",
        marker=dict(size=14, color=driver_color),
        text=[driver],
        textposition="top center",
        showlegend=False
    )

    frames = [
        go.Frame(
            data=[
                go.Scatter(
                    x=[x[k]],
                    y=[y[k]],
                    mode="markers+text",
                    marker=dict(size=14, color=driver_color),
                    text=[driver],
                    textposition="top center"
                )
            ],
            traces=[3]  # último trace é o marcador
        )
        for k in range(len(x))
    ]

    fig = go.Figure(
        data=traces + [marker],
        layout=go.Layout(
            title="Simulação da Volta Mais Rápida",
            height=600,
            xaxis=dict(
                visible=False,
                scaleanchor="y",
                scaleratio=1
            ),
            yaxis=dict(visible=False),
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                buttons=[dict(
                    label="▶ Play",
                    method="animate",
                    args=[None, {
                        "frame": {"duration": 15, "redraw": False},
                        "fromcurrent": True,
                        "transition": {"duration": 0},
                        "mode": "immediate"
                    }]
                )],
                bgcolor="green",
                font=dict(color="white")
            )]
        ),
        frames=frames
    )

    return fig

def plot_all_race_laps_overview(laps, selected_driver=None):

    fastest_lap = laps['LapTimeSeconds'].min()

    fig = go.Figure()

    for driver in laps['Driver'].unique():

        driver_data = laps[laps['Driver'] == driver]

        opacity = 0.3
        width = 1

        if driver == selected_driver:
            opacity = 1
            width = 3

        fig.add_trace(go.Scatter(
            x=driver_data['LapNumber'],
            y=driver_data['LapTimeSeconds'],
            mode='lines',
            line=dict(width=width),
            opacity=opacity,
            name=driver
        ))

    fastest = laps[laps['LapTimeSeconds'] == fastest_lap]

    fig.add_trace(go.Scatter(
        x=fastest['LapNumber'],
        y=fastest['LapTimeSeconds'],
        mode='markers',
        marker=dict(color='purple', size=12),
        name="Fastest Lap"
    ))

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Lap",
        yaxis_title="Lap Time (s)"
    )

    return fig

def render_driver_table(laps, driver):

    driver_laps = laps[laps['Driver'] == driver].copy()

    driver_laps['LapNumber'] = driver_laps['LapNumber'].astype(int)

    #Mais rápido da corrida
    fastest_overall = laps['LapTimeSeconds'].min()

    #Melhor volta pessoal do piloto
    fastest_personal = driver_laps['LapTimeSeconds'].min()

    tolerance = 0.001

    driver_laps["IsFastestOverall"] = np.isclose(
        driver_laps["LapTimeSeconds"],
        fastest_overall,
        atol=tolerance
    )

    driver_laps["IsFastestPersonal"] = np.isclose(
        driver_laps["LapTimeSeconds"],
        fastest_personal,
        atol=tolerance
    )

    #Formatação de tempo
    driver_laps['LapTimeFormatted'] = driver_laps['LapTimeSeconds'].apply(
        lambda x: f"{int(x//60)}:{x%60:06.3f}"
    )

    tyre_map = {
        "SOFT": "🔴 SOFT",
        "MEDIUM": "🟡 MEDIUM",
        "HARD": "⚪ HARD",
        "INTERMEDIATE": "🟢 INTER",
        "WET": "🔵 WET"
    }

    driver_laps["Tyre"] = driver_laps["Compound"].map(tyre_map)

    #Badge textual
    driver_laps.loc[
        driver_laps["IsFastestOverall"],
        "LapTimeFormatted"
    ] += " 🟣 FASTEST"

    driver_laps.loc[
        (driver_laps["IsFastestPersonal"]) &
        (~driver_laps["IsFastestOverall"]),
        "LapTimeFormatted"
    ] += " 🟡 BEST PERSONAL"

    display_df = driver_laps[
        ["LapNumber", "LapTimeFormatted", "Tyre"]
    ]

    #Estilização
    def highlight(row):
        idx = row.name

        if driver_laps.loc[idx, "IsFastestOverall"]:
            return ['background-color: #6f00ff; color: white; font-weight: bold'] * len(row)

        elif driver_laps.loc[idx, "IsFastestPersonal"]:
            return ['background-color: #ffd700; color: black; font-weight: bold'] * len(row)

        return [''] * len(row)

    styled = display_df.style.apply(highlight, axis=1)

    st.dataframe(
        styled,
        use_container_width=True,
        height=500
    )

def plot_animated_circuit_comparison(
    x1, y1, t1, sectors1, driver1,
    x2, y2, t2, sectors2, driver2,
    steps=500,
):
    #cores
    driver1_color = DRIVER_COLORS.get(driver1, "red")
    driver2_color = DRIVER_COLORS.get(driver2, "blue")

    #cores dos setores
    sector_colors = {1: "purple", 2: "green", 3: "yellow"}

    
    t_start = min(t1[0], t2[0])
    t_end = max(t1[-1], t2[-1])
    t_new = np.linspace(t_start, t_end, steps)


    #Interpolação com base no tempo
    x1_interp = np.interp(t_new, t1, x1)
    y1_interp = np.interp(t_new, t1, y1)
    x2_interp = np.interp(t_new, t2, x2)
    y2_interp = np.interp(t_new, t2, y2)

    #ponto inicial comum entre os dois pilotos
    x0 = (x1_interp[0] + x2_interp[0]) / 2
    y0 = (y1_interp[0] + y2_interp[0]) / 2
    x1_interp[0], y1_interp[0] = x0, y0
    x2_interp[0], y2_interp[0] = x0, y0

    #Traçados por setor - piloto 1
    traces = []
    for sector in [1,2,3]:
        mask = sectors1 == sector
        traces.append(go.Scatter(
            x=np.array(x1)[mask],
            y=np.array(y1)[mask],
            mode="lines",
            line=dict(color=sector_colors[sector], width=3),
            showlegend=False
        ))

    # piloto 2 rastro opcional (linhas pontilhadas)
    for sector in [1,2,3]:
        mask = sectors2 == sector
        traces.append(go.Scatter(
            x=np.array(x2)[mask],
            y=np.array(y2)[mask],
            mode="lines",
            line=dict(color=sector_colors[sector], width=3, dash="dot"),
            showlegend=False
        ))

    #Marcadores iniciais
    marker1 = go.Scatter(
        x=[x0], y=[y0],
        mode="markers+text",
        marker=dict(size=14, color=driver1_color),
        text=[driver1],
        textposition="top center",
        showlegend=False
    )
    marker2 = go.Scatter(
        x=[x0], y=[y0],
        mode="markers+text",
        marker=dict(size=14, color=driver2_color),
        text=[driver2],
        textposition="top center",
        showlegend=False
    )

    #Frames da animação
    frames = []
    for k in range(steps):
        frames.append(go.Frame(data=[
            go.Scatter(x=[x1_interp[k]], y=[y1_interp[k]], mode="markers+text",
                       marker=dict(size=14, color=driver1_color), text=[driver1],
                       textposition="top center"),
            go.Scatter(x=[x2_interp[k]], y=[y2_interp[k]], mode="markers+text",
                       marker=dict(size=14, color=driver2_color), text=[driver2],
                       textposition="top center")
        ],
        traces=[len(traces), len(traces)+1]  # apenas os dois marcadores
        ))


    #Layout final
    fig = go.Figure(
        data=traces + [marker1, marker2],
        frames=frames,
        layout=go.Layout(
            title="Comparação de volta mais rápida de cada piloto",
            height=600,
            xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
            yaxis=dict(visible=False),
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                buttons=[dict(
                    label="▶ Play",
                    method="animate",
                    args=[None, {
                        "frame": {"duration": 15, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": 0},
                        "mode": "immediate"
                    }]
                )],
                bgcolor="green",
                font=dict(color="white")
            )]
        )
    )

    return fig


    