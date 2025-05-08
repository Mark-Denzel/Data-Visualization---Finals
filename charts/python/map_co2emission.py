import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from typing import Optional

class CO2EmissionsVisualizer:
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.app = None
        
        self.YEAR_COL = 'Year'
        self.COUNTRY_COL = 'Entity'
        self.CODE_COL = 'Code'
        self.EMISSIONS_COL = 'Annual CO₂ emissions'
        
        self.MIN_EMISSIONS = 0
        self.MAX_EMISSIONS = 10_000_000_000
        
        self.COLOR_SCALE = [
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
        
        self.THRESHOLDS = [
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
        
        self.TICKTEXTS = ['0', '3m', '10m', '30m', '100m', '300m', '1b', '3b', '10b']
        
    def load_data(self) -> bool:
        try:
            self.df = pd.read_csv(self.data_path)
            
            if not all(col in self.df.columns for col in [self.YEAR_COL, self.COUNTRY_COL, self.EMISSIONS_COL]):
                raise ValueError("Required columns not found in the dataset")
                
            self.df[self.YEAR_COL] = pd.to_numeric(self.df[self.YEAR_COL], errors='coerce')
            self.df[self.EMISSIONS_COL] = pd.to_numeric(self.df[self.EMISSIONS_COL], errors='coerce')
            
            self.df = self.df.dropna(subset=[self.YEAR_COL, self.EMISSIONS_COL])
            
            min_year = int(self.df[self.YEAR_COL].min())
            max_year = int(self.df[self.YEAR_COL].max())

            if (self.df[self.EMISSIONS_COL].min() < self.MIN_EMISSIONS or 
                self.df[self.EMISSIONS_COL].max() > self.MAX_EMISSIONS):
                print(f"Warning: CO2 emissions data contains values outside the custom range ({self.MIN_EMISSIONS}-{self.MAX_EMISSIONS} tons)")
            
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
            html.H1("Global CO₂ Emissions Map", className='header'),
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
        ], className='main-container')
        
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        @self.app.callback(
            Output('emissions-map', 'figure'),
            Input('year-slider', 'value')
        )
        def update_map(selected_year: int) -> dict:
            filtered_df = self.df[self.df[self.YEAR_COL] == selected_year]
            
            fig = px.choropleth(
                filtered_df,
                locations=self.COUNTRY_COL,
                color=self.EMISSIONS_COL,
                hover_name=self.COUNTRY_COL,
                hover_data={self.EMISSIONS_COL: ':,.0f', self.CODE_COL: True},
                title=f'Global CO₂ Emissions in {selected_year}',
                color_continuous_scale=self.COLOR_SCALE,
                projection='natural earth',
                locationmode='country names',
                range_color=[self.MIN_EMISSIONS, self.MAX_EMISSIONS]
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
                    title='CO₂ Emissions (tons)',
                    ticks='outside',
                    tickvals=self.THRESHOLDS,
                    ticktext=self.TICKTEXTS,
                    lenmode='pixels',
                    len=400,
                    thickness=20,
                    yanchor='middle',
                    y=0.5,
                    xanchor='right',
                    x=1.05,
                    ticklen=10,
                    tickfont=dict(size=12)
                )
            )
            
            return fig
    
    def run(self, debug: bool = False) -> None:
        if self.app is None:
            raise ValueError("App not created. Call create_app() first.")
            
        if debug:
            print("Data preview:")
            print(self.df.head())
            print(f"\nCO2 emissions range in data: {self.df[self.EMISSIONS_COL].min():,} to {self.df[self.EMISSIONS_COL].max():,} tons")
            print(f"Year range: {self.df[self.YEAR_COL].min()} to {self.df[self.YEAR_COL].max()}")
            
        self.app.run(debug=debug)

def main():
    DATA_FILE = "datasets/yearly-co2-emissions.csv"
    
    visualizer = CO2EmissionsVisualizer(DATA_FILE)
    
    if visualizer.load_data():
        visualizer.create_app()
        visualizer.run(debug=True)
    else:
        print("Failed to initialize application due to data loading errors.")

if __name__ == '__main__':
    main()