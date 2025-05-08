# charts/python/dash_co2map.py

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import numpy as np

DATA_FILE = "datasets/yearly-co2-emissions.csv"
df = pd.read_csv(DATA_FILE)

# Clean and preprocess
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df['Annual CO₂ emissions'] = pd.to_numeric(df['Annual CO₂ emissions'], errors='coerce')
df = df.dropna(subset=['Year', 'Annual CO₂ emissions'])
df['Log Emissions'] = np.log10(df['Annual CO₂ emissions'].replace(0, np.nan))

MIN_EMISSIONS = 0
MAX_EMISSIONS = 10_000_000_000

COLOR_SCALE = [
    [0.0, "#FFF5F0"],
    [0.0003, "#FEE0D2"],
    [0.001, "#FCBBA1"],
    [0.003, "#FC9272"],
    [0.01, "#FB6A4A"],
    [0.03, "#EF3B2C"],
    [0.1, "#CB181D"],
    [0.3, "#67000D"],
    [1.0, "#67000D"]
]

THRESHOLDS = [
    0,
    3_000_000,
    10_000_000,
    30_000_000,
    100_000_000,
    300_000_000,
    1_000_000_000,
    3_000_000_000,
    10_000_000_000
]

TICKTEXTS = ['0', '3m', '10m', '30m', '100m', '300m', '1b', '3b', '10b']

# Create Dash app
app = Dash(__name__, requests_pathname_prefix='/co2/')
server = app.server

min_year = int(df['Year'].min())
max_year = int(df['Year'].max())

app.layout = html.Div([
    html.H1("Global CO₂ Emissions Map", className='header'),
    html.Div([
        dcc.Slider(
            id='year-slider',
            min=min_year,
            max=max_year,
            value=min_year,
            marks=None,
            step=1,
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], className='slider-container'),
    dcc.Graph(id='emissions-map', className='map-container'),
    html.Div([
        html.P("CO₂ Emissions Color Scale", style={'text-align': 'center', 'margin-bottom': '5px'}),
        html.Div([
            html.Span("0", style={'float': 'left', 'margin-left': '5%'}),
            html.Span("3m", style={'float': 'left', 'margin-left': '7%'}),
            html.Span("10m", style={'float': 'left', 'margin-left': '7%'}),
            html.Span("30m", style={'float': 'left', 'margin-left': '6%'}),
            html.Span("100m", style={'float': 'left', 'margin-left': '5%'}),
            html.Span("300m", style={'float': 'left', 'margin-left': '4%'}),
            html.Span("1b", style={'float': 'left', 'margin-left': '5%'}),
            html.Span("3b", style={'float': 'left', 'margin-left': '5%'}),
            html.Span("10b", style={'float': 'right', 'margin-right': '5%'})
        ], style={
            'background': 'linear-gradient(to right, #FFF5F0, #FEE0D2, #FCBBA1, #FC9272, #FB6A4A, #EF3B2C, #CB181D, #67000D)',
            'height': '30px',
            'width': '90%',
            'margin': '0 auto',
            'border-radius': '5px'
        })
    ], style={'text-align': 'center', 'width': '100%', 'margin': '20px auto'})
])

@app.callback(
    Output('emissions-map', 'figure'),
    Input('year-slider', 'value')
)
def update_map(selected_year: int):
    filtered_df = df[df['Year'] == selected_year].copy()
    filtered_df['Log Emissions'] = np.log10(filtered_df['Annual CO₂ emissions'].replace(0, np.nan))

    fig = px.choropleth(
        filtered_df,
        locations='Entity',
        locationmode='country names',
        color='Log Emissions',
        hover_name='Entity',
        hover_data={'Annual CO₂ emissions': ':,.0f', 'Code': True},
        color_continuous_scale=COLOR_SCALE,
        range_color=[np.log10(THRESHOLDS[1]), np.log10(MAX_EMISSIONS)],
        projection='natural earth',
        title=f"Global CO₂ Emissions in {selected_year}"
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
        height=600,
        margin={"r": 40, "t": 40, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title='CO₂ Emissions (tons)',
            ticks='outside',
            tickvals=np.log10(THRESHOLDS[1:]),  # skip zero
            ticktext=TICKTEXTS,
            lenmode='pixels',
            len=400,
            thickness=20,
            yanchor='middle',
            y=0.5,
            xanchor='right',
            x=1.25,
            ticklen=10,
            tickfont=dict(size=12)
        )
    )

    return fig
