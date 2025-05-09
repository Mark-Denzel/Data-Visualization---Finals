import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from typing import Optional

class GlobalTemperatureVisualizer:
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.app = None
        
        self.YEAR_COL = 'year'
        self.COUNTRY_COL = 'Entity'
        self.TEMP_COL = 'Average surface temperature'
        
        self.MIN_TEMP = -15
        self.MAX_TEMP = 30
        self.COLOR_SCALE = [
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
        
    def load_data(self) -> bool:
        try:
            self.df = pd.read_csv(self.data_path)
            
            if not all(col in self.df.columns for col in [self.YEAR_COL, self.COUNTRY_COL, self.TEMP_COL]):
                raise ValueError("Required columns not found in the dataset")
                
            self.df[self.YEAR_COL] = pd.to_numeric(self.df[self.YEAR_COL], errors='coerce')
            self.df[self.TEMP_COL] = pd.to_numeric(self.df[self.TEMP_COL], errors='coerce')
            self.df = self.df[(self.df[self.YEAR_COL] >= 1940) & (self.df[self.YEAR_COL] <= 2024)]

            if (self.df[self.TEMP_COL].min() < self.MIN_TEMP or 
                self.df[self.TEMP_COL].max() > self.MAX_TEMP):
                print(f"Warning: Temperature data contains values outside the custom range ({self.MIN_TEMP}-{self.MAX_TEMP}°C)")
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_app(self) -> None:
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        self.app = Dash(__name__)
        
        min_year = int(self.df[self.YEAR_COL].min())
        max_year = int(self.df[self.YEAR_COL].max())
        
        self.app.layout = html.Div([
            html.H1("Global Temperature Map (1940-2024)", className='header'),
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
            html.Div([
                html.Img(src='assets/color_scale_legend.png', style={'height':'30px', 'width':'100%'})
            ], style={'text-align': 'center'})
        ], className='main-container')
        
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        @self.app.callback(
            Output('temperature-map', 'figure'),
            Input('year-slider', 'value')
        )
        def update_map(selected_year: int) -> dict:
            filtered_df = self.df[self.df[self.YEAR_COL] == selected_year]
            
            fig = px.choropleth(
                filtered_df,
                locations=self.COUNTRY_COL,
                color=self.TEMP_COL,
                hover_name=self.COUNTRY_COL,
                hover_data={self.TEMP_COL: ':.2f', 'Code': True},
                title=f'Global Temperatures in {selected_year}',
                color_continuous_scale=self.COLOR_SCALE,
                projection='natural earth',
                locationmode='country names',
                range_color=[self.MIN_TEMP, self.MAX_TEMP]
            )
            
            fig.update_layout(
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    projection_type='equirectangular'
                ),
                height=600,
                margin={"r": 0, "t": 40, "l": 0, "b": 0},
                coloraxis_colorbar=dict(
                    title='Temperature (°C)',
                    ticks='outside',
                    tickvals=[-15, -10, -5, 0, 5, 10, 15, 20, 25, 30],
                    ticktext=['-15°C', '-10°C', '-5°C', '0°C', '5°C', '10°C', '15°C', '20°C', '25°C', '30°C'],
                )
            )
            
            return fig
    
    def run(self, debug: bool = False) -> None:
        if self.app is None:
            raise ValueError("App not created. Call create_app() first.")
            
        if debug:
            print("Data preview:")
            print(self.df.head())
            print(f"\nTemperature range in data: {self.df[self.TEMP_COL].min()}°C to {self.df[self.TEMP_COL].max()}°C")
            
        self.app.run(debug=debug)

def main():
    DATA_FILE = "datasets/yearl_temperature.csv"
    
    visualizer = GlobalTemperatureVisualizer(DATA_FILE)
    
    if visualizer.load_data():
        visualizer.create_app()
        visualizer.run(debug=True)
    else:
        print("Failed to initialize application due to data loading errors.")

if __name__ == '__main__':
    main()