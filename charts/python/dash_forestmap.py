# charts/python/dash_forestmap.py

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Constants
DATA_FILE = "datasets/map_forest_area.csv"
YEAR_COL = 'Year'
COUNTRY_COL = 'Entity'
CODE_COL = 'Code'
FOREST_COL = 'Forest area'

# Color scale and thresholds
COLOR_SCALE_BREAKPOINTS = [
    500_000, 1_000_000, 5_000_000, 10_000_000,
    50_000_000, 100_000_000, 500_000_000, 1_000_000_000
]
TICKTEXT = ['500k', '1m', '5m', '10m', '50m', '100m', '500m', '1b']
COLOR_SCALE = [
    [0.0, "#ffffcc"],
    [0.1, "#c2e699"],
    [0.2, "#78c679"],
    [0.3, "#31a354"],
    [0.4, "#006837"],
    [0.6, "#004529"],
    [0.8, "#003420"],
    [1.0, "#002010"]
]

# Load and preprocess
df = pd.read_csv(DATA_FILE)
df[YEAR_COL] = pd.to_numeric(df[YEAR_COL], errors='coerce')
df[FOREST_COL] = pd.to_numeric(df[FOREST_COL], errors='coerce')
df = df[df[YEAR_COL].between(1990, 2020)]

# Create Dash app
app = Dash(__name__, requests_pathname_prefix='/forest/')
server = app.server

min_year = int(df[YEAR_COL].min())
max_year = int(df[YEAR_COL].max())

app.layout = html.Div([
    html.H1("Global Forest Area (1990–2020)", className='header'),
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
    dcc.Graph(id='forest-map', className='map-container')
], className='main-container')

@app.callback(
    Output('forest-map', 'figure'),
    Input('year-slider', 'value')
)
def update_map(selected_year: int):
    filtered_df = df[df[YEAR_COL] == selected_year]
    
    fig = px.choropleth(
        filtered_df,
        locations=CODE_COL,
        color=FOREST_COL,
        hover_name=COUNTRY_COL,
        hover_data={FOREST_COL: ':,.0f', CODE_COL: False},
        title=f"Global Forest Area in {selected_year}",
        color_continuous_scale=COLOR_SCALE,
        projection='natural earth',
        locationmode='ISO-3',
        range_color=[0, max(COLOR_SCALE_BREAKPOINTS)]
    )
    
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
        height=600,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title='Forest Area (Hectares)',
            ticks='outside',
            tickvals=COLOR_SCALE_BREAKPOINTS,
            ticktext=TICKTEXT
        )
    )
    
    return fig
