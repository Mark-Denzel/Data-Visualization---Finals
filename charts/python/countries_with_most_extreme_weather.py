from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os

app = Dash(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join('datasets/Climate_Change_Dataset.csv')

try:
    df = pd.read_csv(csv_path)
    
    # Aggregate extreme weather events by country (summing all years 2000-2023)
    aggregated_df = df.groupby('Country', as_index=False)['Extreme Weather Events'].sum()
    
    # Get unique countries for dropdown
    countries = aggregated_df['Country'].unique()
    
    app.layout = html.Div([
        html.Div([
            html.H1("Total Extreme Weather Events (2000-2023)", 
                   style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif', 'marginBottom': '20px',}),
            html.Div([
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} for country in sorted(countries)],
                    multi=True,  # Enable multiple selection
                    placeholder="Select one or more countries...",
                    style={'width': '50%', 'margin': '0 auto', 'fontFamily': 'Arial, sans-serif'}
                )
            ], style={'marginBottom': '30px'}),
        ], style={'backgroundColor': '#f9f9f9', 'padding': '20px', 'borderRadius': '5px'}),
        
        dcc.Graph(
            id='weather-events-chart',
            config={
                'scrollZoom': False,
                'displayModeBar': False,
            },
            style={'height': '600px', 'width': '100%', 'maxWidth': '1200px'}
        )
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})
    
    @app.callback(
        Output('weather-events-chart', 'figure'),
        Input('country-dropdown', 'value')
    )
    def update_graph(selected_countries):
        # Filter data based on selected countries
        if selected_countries:
            filtered_df = aggregated_df[aggregated_df['Country'].isin(selected_countries)]
        else:
            filtered_df = aggregated_df
        
        # Calculate y-axis max with some padding
        y_max = filtered_df['Extreme Weather Events'].max() * 1.1 if not filtered_df.empty else 100
        
        fig = px.bar(filtered_df, 
                     x='Country', 
                     y='Extreme Weather Events',
                     labels={'Extreme Weather Events': 'Total Events', 'Country': 'Country'},
                     color='Country')
        
        fig.update_layout(
            xaxis_title='Country',
            yaxis_title='Total Extreme Weather Events',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=12, color='#333'),
            margin=dict(l=50, r=50, b=50, t=80, pad=4),
            hovermode='x unified',
            title={
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 18}
            },
            xaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=2,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='rgb(82, 82, 82)',
                ),
                gridcolor='rgb(240, 240, 240)',
                fixedrange=True
            ),
            yaxis=dict(
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=2,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='rgb(82, 82, 82)',
                ),
                gridcolor='rgb(240, 240, 240)',
                range=[0, y_max],
                autorange=False,
                fixedrange=True
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
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

if __name__ == '__main__':
    app.run(debug=True)