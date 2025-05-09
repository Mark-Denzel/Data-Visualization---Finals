from flask import Flask, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# Visualizations
# Maps
from charts.python.maps.dash_co2map import server as dash_co2_server
from charts.python.maps.dash_forestmap import server as dash_forest_server
from charts.python.maps.dash_airquality import server as dash_aqi_server
from charts.python.maps.dash_temperaturemap import server as dash_temperature_server

# Heat Maps
from charts.python.heatmaps.dash_correlation_pollution import server as dash_correlation_polution_server
from charts.python.heatmaps.dash_correlation_climate_change import server as dash_correlation_climate_change_server

#Bar Chart
from charts.python.timeseriescharts.dash_weather_server import server as dash_weather_server

# Line Graph
from charts.python.timeseriescharts.dash_plastic_waste import server as dash_plastic_server

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/datasets')
def datasets():
    return render_template('datasets.html')

@app.route('/worldmap')
def worldmap():
    return render_template('worldmap.html')

# Mount Dash under /dash
application = DispatcherMiddleware(app, {
    # Correlation Heatmaps
    "/dash": dash_correlation_polution_server,
    "/climate": dash_correlation_climate_change_server,
    
    # Maps
    "/co2": dash_co2_server,
    "/forest": dash_forest_server,
    "/aqi": dash_aqi_server,
    "/temperature": dash_temperature_server,
    
    # Bar Charts
    "/weather-events": dash_weather_server,
    
    # Line Graph
    "/plastic-waste": dash_plastic_server
})

if __name__ == "__main__":
    run_simple("localhost", 5000, application, use_reloader=True, use_debugger=True)
