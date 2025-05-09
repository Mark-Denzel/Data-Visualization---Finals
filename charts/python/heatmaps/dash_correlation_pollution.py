import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

df = pd.read_csv('datasets/Pollution_Dataset.csv')

df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
df['Year'] = df['Date'].dt.year

# Exclude non-numeric columns for correlation
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols = [col for col in numeric_cols if col not in ['Year']]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], requests_pathname_prefix="/dash/")
server = app.server 

app.layout = dbc.Container([
    html.H1("Environmental Pollution Data Correlation Analysis", className="mb-4 text-center"),
    
    dbc.Row([
        dbc.Col([
            html.Label("Select Year Range:", className="mb-2"),
            dcc.RangeSlider(
                id='year-slider',
                min=int(df['Year'].min()),
                max=int(df['Year'].max()),
                step=1,
                value=[int(df['Year'].min()), int(df['Year'].max())],
                marks={int(year): str(int(year)) for year in sorted(df['Year'].dropna().unique())},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='correlation-heatmap')
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3("Correlation Interpretation Guide:", className="mt-4"),
                html.Ul([
                    html.Li("+1: Perfect positive correlation"),
                    html.Li("+0.5 to +0.9: Strong positive correlation"),
                    html.Li("+0.3 to +0.5: Moderate positive correlation"),
                    html.Li("-0.3 to +0.3: Weak or no correlation"),
                    html.Li("-0.5 to -0.3: Moderate negative correlation"),
                    html.Li("-0.9 to -0.5: Strong negative correlation"),
                    html.Li("-1: Perfect negative correlation")
                ])
            ], className="mt-4 p-3 bg-light rounded")
        ], width=12)
    ])
], fluid=True)

@app.callback(
    Output('correlation-heatmap', 'figure'),
    Input('year-slider', 'value')
)
def update_heatmap(year_range):
    # Filter data by year range
    filtered_df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

    # Drop rows with NaNs in relevant numeric columns
    filtered_df = filtered_df.dropna(subset=numeric_cols)

    # Group by year and aggregate using mean to reduce daily noise
    aggregated_df = filtered_df.groupby('Year')[numeric_cols].mean().reset_index()

    # Compute correlation matrix
    corr_matrix = aggregated_df[numeric_cols].corr()

    # Create heatmap
    fig = px.imshow(
        corr_matrix,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        color_continuous_scale='RdBu',
        zmin=-1,
        zmax=1,
        title=f"Correlation Between Environmental Factors ({year_range[0]} - {year_range[1]})",
        text_auto=".2f"
    )

    fig.update_layout(
        height=800,
        width=1000,
        xaxis_title="Environmental Factors",
        yaxis_title="Environmental Factors",
        coloraxis_colorbar=dict(title="Correlation"),
        font=dict(size=10)
    )
    
    fig.update_xaxes(tickangle=45)
    fig.update_traces(hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.2f}<extra></extra>")
    
    return fig

