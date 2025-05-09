from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os

app = Dash(__name__, requests_pathname_prefix='/plastic-waste/')
server = app.server

csv_path = os.path.join('datasets/plastic_waste_VS_recycled..csv')

try:
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    countries = df['Country'].unique()

    app.layout = html.Div([
        html.Div([
            html.H1("Plastic Waste vs Plastic Recycled", 
                    style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif', 'color': '#fff',
                           'marginBottom': '20px'}),
            html.Div([
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} for country in sorted(countries)],
                    value='Philippines',
                    style={'width': '50%', 'margin': '0 auto', 'fontFamily': 'Arial, sans-serif'}
                )
            ], style={'marginBottom': '30px'}),
        ], style={'backgroundColor': '#1f2937', 'padding': '20px', 'borderRadius': '8px'}),

        dcc.Graph(
            id='waste-recycled-chart',
            config={'scrollZoom': True, 'displayModeBar': False},
            style={'height': '600px', 'width': '100%', 'maxWidth': '1200px'}
        )
    ], style={
        'backgroundColor': '#111827',
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '20px',
        'borderRadius': '8px'
    })

    @app.callback(
        Output('waste-recycled-chart', 'figure'),
        Input('country-dropdown', 'value')
    )
    def update_graph(selected_country):
        filtered_df = df[df['Country'] == selected_country]
        y_max = max(filtered_df['Plastic_Waste_Tons'].max(), filtered_df['Plastic_Recycled_Tons'].max()) * 1.1
        x_min, x_max = filtered_df['Date'].min(), filtered_df['Date'].max()

        fig = px.line(filtered_df, 
                      x='Date', 
                      y=['Plastic_Waste_Tons', 'Plastic_Recycled_Tons'],
                      title=f'Plastic Waste vs Recycled in {selected_country}',
                      labels={'value': 'Tons', 'variable': 'Metric'},
                      color_discrete_map={
                          'Plastic_Waste_Tons': 'red',
                          'Plastic_Recycled_Tons': '#4ECDC4'
                      })

        fig.update_layout(
            plot_bgcolor='#111827',
            paper_bgcolor='#111827',
            font=dict(color='#E5E7EB'),
            xaxis=dict(
                title='Date',
                gridcolor='rgba(255,255,255,0.05)',
                tickfont=dict(size=12),
                linecolor='gray',
                range=[x_min, x_max],
                fixedrange=False
            ),
            yaxis=dict(
                title='Tons of Plastic',
                gridcolor='rgba(255,255,255,0.05)',
                tickfont=dict(size=12),
                range=[0, y_max],
                fixedrange=False
            ),
            title=dict(
                x=0.5,
                font=dict(size=18)
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            margin=dict(l=40, r=40, t=60, b=60)
        )

        return fig

except FileNotFoundError:
    app.layout = html.Div([
        html.H1("Error: File Not Found"),
        html.P(f"Could not find the data file at: {csv_path}"),
        html.P("Please check the file path and try again.")
    ])
except Exception as e:
    app.layout = html.Div([
        html.H1("Error Loading Data"),
        html.P(str(e))
    ])
