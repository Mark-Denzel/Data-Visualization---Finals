import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from typing import Optional

class ForestAreaVisualizer:
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.app = None
        
        self.YEAR_COL = 'Year'
        self.COUNTRY_COL = 'Entity'
        self.CODE_COL = 'Code'
        self.FOREST_COL = 'Forest area'
        
        self.COLOR_SCALE_BREAKPOINTS = [
            500000,
            1000000,
            5000000,
            10000000,
            50000000,
            100000000,
            500000000,
            1000000000
        ]
        
        self.COLOR_SCALE = [
            [0.0, "#ffffcc"],
            [0.1, "#c2e699"],
            [0.2, "#78c679"],
            [0.3, "#31a354"],
            [0.4, "#006837"],
            [0.6, "#004529"],
            [0.8, "#003420"],
            [1.0, "#002010"]
        ]
        
    def load_data(self) -> bool:
        try:
            self.df = pd.read_csv(self.data_path)
            
            if not all(col in self.df.columns for col in [self.YEAR_COL, self.COUNTRY_COL, self.FOREST_COL, self.CODE_COL]):
                raise ValueError("Required columns not found in the dataset")
                
            self.df[self.YEAR_COL] = pd.to_numeric(self.df[self.YEAR_COL], errors='coerce')
            self.df[self.FOREST_COL] = pd.to_numeric(self.df[self.FOREST_COL], errors='coerce')
            
            self.df = self.df[(self.df[self.YEAR_COL] >= 1990) & (self.df[self.YEAR_COL] <= 2020)]
            
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
            html.H1("Global Forest Area (1990-2020)", className='header'),
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
        
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        @self.app.callback(
            Output('forest-map', 'figure'),
            Input('year-slider', 'value')
        )
        def update_map(selected_year: int) -> dict:
            filtered_df = self.df[self.df[self.YEAR_COL] == selected_year]
            
            tickvals = self.COLOR_SCALE_BREAKPOINTS
            ticktext = [
                '500k', '1m', '5m', '10m', 
                '50m', '100m', '500m', '1b'
            ]
            
            range_min = 0
            range_max = max(self.COLOR_SCALE_BREAKPOINTS)
            
            fig = px.choropleth(
                filtered_df,
                locations=self.CODE_COL,
                color=self.FOREST_COL,
                hover_name=self.COUNTRY_COL,
                hover_data={self.FOREST_COL: ':,.0f', self.CODE_COL: False},
                title=f'Global Forest Area in {selected_year}',
                color_continuous_scale=self.COLOR_SCALE,
                projection='natural earth',
                locationmode='ISO-3',
                range_color=[range_min, range_max]
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
                    title='Forest Area (Hectares)',
                    ticks='outside',
                    tickvals=tickvals,
                    ticktext=ticktext
                )
            )
            
            return fig
    
    def run(self, debug: bool = False) -> None:
        if self.app is None:
            raise ValueError("App not created. Call create_app() first.")
            
        if debug:
            print("Data preview:")
            print(self.df.head())
            print(f"\nForest area range in data: {self.df[self.FOREST_COL].min():,} to {self.df[self.FOREST_COL].max():,} hectares")
            print(f"Years available: {self.df[self.YEAR_COL].min()} to {self.df[self.YEAR_COL].max()}")
            
        self.app.run(debug=debug)

def main():
    DATA_FILE = "datasets/map_forest_area.csv"
    
    visualizer = ForestAreaVisualizer(DATA_FILE)
    
    if visualizer.load_data():
        visualizer.create_app()
        visualizer.run(debug=True)
    else:
        print("Failed to initialize application due to data loading errors.")

if __name__ == '__main__':
    main()