# charts/python/dash_aqi_map.py

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from datetime import datetime

DATA_FILE = "datasets/map_air_quality.csv"

DATE_COL = 'Date'
COUNTRY_COL = 'Country'
STATUS_COL = 'Status'
AQI_COL = 'AQI Value'

MIN_AQI = 0
MAX_AQI = 500

COLOR_SCALE = [
    [0.0, "#00E400"],
    [0.1, "#FFFF00"],
    [0.2, "#FF7E00"],
    [0.3, "#FF0000"],
    [0.6, "#8F3F97"],
    [1.0, "#7E0023"]
]

# Load and clean data
df = pd.read_csv(DATA_FILE)
df[DATE_COL] = pd.to_datetime(df[DATE_COL])
df[AQI_COL] = pd.to_numeric(df[AQI_COL], errors='coerce')
df = df[
    (df[DATE_COL] >= pd.to_datetime('2022-07-21')) &
    (df[DATE_COL] <= pd.to_datetime('2025-05-08'))
]

# Initialize Dash
app = Dash(__name__, requests_pathname_prefix='/aqi/')
server = app.server

unique_dates = sorted(df[DATE_COL].unique())
min_date = unique_dates[0]
max_date = unique_dates[-1]

app.layout = html.Div([
    html.H1("Global Air Quality Index (AQI) Map", className='header'),
    html.Div([
        dcc.Slider(
            id='date-slider',
            min=0,
            max=len(unique_dates) - 1,
            value=0,
            marks=None,
            step=1,
            tooltip={"placement": "bottom", "always_visible": True},
            updatemode='drag'
        )
    ], className='slider-container'),
    dcc.Graph(id='aqi-map', className='map-container')
], className='main-container')

@app.callback(
    Output('aqi-map', 'figure'),
    Input('date-slider', 'value')
)
def update_map(selected_date_idx: int):
    selected_date = unique_dates[selected_date_idx]
    filtered_df = df[df[DATE_COL] == selected_date]

    fig = px.choropleth(
        filtered_df,
        locations=COUNTRY_COL,
        color=AQI_COL,
        hover_name=COUNTRY_COL,
        hover_data={AQI_COL: ':.0f', STATUS_COL: True},
        title=f'Global Air Quality Index on {selected_date.strftime("%Y-%m-%d")}',
        color_continuous_scale=COLOR_SCALE,
        projection='natural earth',
        locationmode='country names',
        range_color=[MIN_AQI, MAX_AQI]
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
        height=600,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title='AQI Value',
            ticks='outside',
            tickvals=[0, 50, 100, 150, 200, 300, 400, 500],
            ticktext=[
                '0',
                '50 (Good)',
                '100 (Moderate)',
                '150 (Unhealthy for Sensitive)',
                '200 (Unhealthy)',
                '300 (Very Unhealthy)',
                '400 (Hazardous)',
                '500 (Severe)'
            ]
        )
    )

    return fig
