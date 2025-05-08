import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from typing import Optional
from datetime import datetime

class ForestAreaVisualizer:
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.app = None
        
        self.DATE_COL = 'Date'
        self.COUNTRY_COL = 'Country'
        self.STATUS_COL = 'Status'
        self.AQI_COL = 'AQI Value'
        
        self.MIN_AQI = 0
        self.MAX_AQI = 500
        self.COLOR_SCALE = [
            [0.0, "#00E400"],
            [0.1, "#FFFF00"],
            [0.2, "#FF7E00"],
            [0.3, "#FF0000"],
            [0.6, "#8F3F97"],
            [1.0, "#7E0023"]
        ]
        
    def load_data(self) -> bool:
        try:
            self.df = pd.read_csv(self.data_path)
            
            if not all(col in self.df.columns for col in [self.DATE_COL, self.COUNTRY_COL, self.AQI_COL]):
                raise ValueError("Required columns not found in the dataset")
                
            self.df[self.DATE_COL] = pd.to_datetime(self.df[self.DATE_COL])
            self.df[self.AQI_COL] = pd.to_numeric(self.df[self.AQI_COL], errors='coerce')
            
            start_date = pd.to_datetime('2022-07-21')
            end_date = pd.to_datetime('2025-05-08')
            self.df = self.df[(self.df[self.DATE_COL] >= start_date) & 
                             (self.df[self.DATE_COL] <= end_date)]

            if (self.df[self.AQI_COL].min() < self.MIN_AQI or 
                self.df[self.AQI_COL].max() > self.MAX_AQI):
                print(f"Warning: AQI data contains values outside the custom range ({self.MIN_AQI}-{self.MAX_AQI})")
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_app(self) -> None:
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        self.app = Dash(__name__)
        
        min_date = self.df[self.DATE_COL].min().to_pydatetime()
        max_date = self.df[self.DATE_COL].max().to_pydatetime()
        
        self.app.layout = html.Div([
            html.H1("Global Air Quality Index (AQI) Map", className='header'),
            html.Div([
                dcc.Slider(
                    id='date-slider',
                    min=0,
                    max=len(self.df[self.DATE_COL].unique()) - 1,
                    value=0,
                    marks=None,
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": True},
                    updatemode='drag'
                )
            ], className='slider-container'),
            dcc.Graph(id='aqi-map', className='map-container')
        ], className='main-container')
        
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        @self.app.callback(
            Output('aqi-map', 'figure'),
            Input('date-slider', 'value')
        )
        def update_map(selected_date_idx: int) -> dict:
            unique_dates = sorted(self.df[self.DATE_COL].unique())
            selected_date = unique_dates[selected_date_idx]
            filtered_df = self.df[self.df[self.DATE_COL] == selected_date]
            
            fig = px.choropleth(
                filtered_df,
                locations=self.COUNTRY_COL,
                color=self.AQI_COL,
                hover_name=self.COUNTRY_COL,
                hover_data={self.AQI_COL: ':.0f', self.STATUS_COL: True},
                title=f'Global Air Quality Index on {selected_date.strftime("%Y-%m-%d")}',
                color_continuous_scale=self.COLOR_SCALE,
                projection='natural earth',
                locationmode='country names',
                range_color=[self.MIN_AQI, self.MAX_AQI]
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
                    ],
                )
            )
            
            return fig
    
    def run(self, debug: bool = False) -> None:
        if self.app is None:
            raise ValueError("App not created. Call create_app() first.")
            
        if debug:
            print("Data preview:")
            print(self.df.head())
            print(f"\nAQI range in data: {self.df[self.AQI_COL].min()} to {self.df[self.AQI_COL].max()}")
            
        self.app.run(debug=debug)

def main():
    DATA_FILE = "datasets/map_air_quality.csv"
    
    visualizer = ForestAreaVisualizer(DATA_FILE)
    
    if visualizer.load_data():
        visualizer.create_app()
        visualizer.run(debug=True)
    else:
        print("Failed to initialize application due to data loading errors.")

if __name__ == '__main__':
    main()