# charts/python/dash_temperature_map.py

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# === Config ===
DATA_FILE = "datasets/yearl_temperature.csv"
YEAR_COL = 'year'
COUNTRY_COL = 'Entity'
TEMP_COL = 'Average surface temperature'
MIN_TEMP = -15
MAX_TEMP = 30
COLOR_SCALE = [
    [0.0, "#313695"],
    [0.2, "#4575B4"],
    [0.4, "#74ADD1"],
    [0.5, "#ABD9E9"],
    [0.6, "#FFFFBF"],
    [0.75, "#FEE090"],
    [0.8, "#FDAE61"],
    [0.9, "#F46D43"],
    [0.95, "#D73027"],
    [1.0, "#A50026"]
]

# === Load Data ===
df = pd.read_csv(DATA_FILE)
df[YEAR_COL] = pd.to_numeric(df[YEAR_COL], errors='coerce')
df[TEMP_COL] = pd.to_numeric(df[TEMP_COL], errors='coerce')
df = df[(df[YEAR_COL] >= 1940) & (df[YEAR_COL] <= 2024)]

# === Init Dash ===
app = Dash(__name__, requests_pathname_prefix='/temperature/')
server = app.server

min_year = int(df[YEAR_COL].min())
max_year = int(df[YEAR_COL].max())

app.layout = html.Div([
    html.H1("Global Temperature Map (1940–2024)", className='header'),
    html.Div([
        dcc.Slider(
            id='year-slider',
            min=min_year,
            max=max_year,
            value=min_year,
            marks=None,
            step=1,
            tooltip={"placement": "bottom", "always_visible": True},
            updatemode='drag'
        )
    ], className='slider-container'),
    dcc.Graph(id='temperature-map', className='map-container'),
], className='main-container')

@app.callback(
    Output('temperature-map', 'figure'),
    Input('year-slider', 'value')
)
def update_map(selected_year):
    filtered_df = df[df[YEAR_COL] == selected_year]
    fig = px.choropleth(
        filtered_df,
        locations=COUNTRY_COL,
        color=TEMP_COL,
        hover_name=COUNTRY_COL,
        hover_data={TEMP_COL: ':.2f'},
        title=f"Global Temperatures in {selected_year}",
        color_continuous_scale=COLOR_SCALE,
        projection='natural earth',
        locationmode='country names',
        range_color=[MIN_TEMP, MAX_TEMP]
    )

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        height=600,
        margin={"r": 0, "t": 40, "l": 0, "b": 80},  # extra bottom space
        coloraxis_colorbar=dict(
            title=dict(
                text='Temperature (°C)',
                font=dict(size=12),
                side='top' 
            ),
            orientation='h',
            ticks='outside',
            tickvals=[-15, -10, -5, 0, 5, 10, 15, 20, 25, 30],
            ticktext=['-15°C', '-10°C', '-5°C', '0°C', '5°C', '10°C', '15°C', '20°C', '25°C', '30°C'],
            len=0.8,
            thickness=20,
            x=0.5,
            xanchor='center',
            y=-0.25,
            yanchor='top',
            ticklen=10,
            tickfont=dict(size=11)
        )
    )


    return fig
