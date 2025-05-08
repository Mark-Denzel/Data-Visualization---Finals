from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os

app = Dash(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join('datasets/plastic_waste_VS_recycled..csv')

try:
    df = pd.read_csv(csv_path)
    
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    
    countries = df['Country'].unique()
    
    app.layout = html.Div([
        html.Div([
            html.H1("Plastic Waste vs Plastic Recycled", 
                   style={'textAlign': 'center', 'fontFamily': 'Arial, sans-serif', 'marginBottom': '20px'}),
            html.Div([
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} for country in sorted(countries)],
                    value='Philippines',
                    style={'width': '50%', 'margin': '0 auto', 'fontFamily': 'Arial, sans-serif'}
                )
            ], style={'marginBottom': '30px'}),
        ], style={'backgroundColor': '#f9f9f9', 'padding': '20px', 'borderRadius': '5px'}),
        
        dcc.Graph(
            id='waste-recycled-chart',
            config={
                'scrollZoom': True,
                'displayModeBar': False,
            },
            style={'height': '600px', 'width': '100%', 'maxWidth': '1200px'}
        )
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})
    
    @app.callback(
        Output('waste-recycled-chart', 'figure'),
        Input('country-dropdown', 'value')
    )
    def update_graph(selected_country):
        filtered_df = df[df['Country'] == selected_country]
        
        y_max = max(filtered_df['Plastic_Waste_Tons'].max(), filtered_df['Plastic_Recycled_Tons'].max()) * 1.1
        x_min = filtered_df['Date'].min()
        x_max = filtered_df['Date'].max()
        
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
            xaxis_title='Date',
            yaxis_title='Tons of Plastic',
            legend_title='Metric',
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
                range=[x_min, x_max],
                autorange=False,
                fixedrange=False
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
                fixedrange=False
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        
        fig.update_layout(
            xaxis=dict(
                minallowed=x_min,
                maxallowed=x_max
            ),
            yaxis=dict(
                minallowed=0,
                maxallowed=y_max
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