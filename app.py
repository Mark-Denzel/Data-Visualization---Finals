from flask import Flask, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from charts.python.dash_correlation_pollution import server as dash_server
from charts.python.dash_co2map import server as dash_co2_server
from charts.python.dash_forestmap import server as dash_forest_server


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
    "/dash": dash_server,
    "/co2": dash_co2_server,
    "/forest": dash_forest_server
})

if __name__ == "__main__":
    run_simple("localhost", 5000, application, use_reloader=True, use_debugger=True)
