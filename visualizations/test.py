import plotly.express as px

fig = px.line(x=[1, 2, 3], y=[10, 20, 30])
fig.write_html("plot_python.html", full_html=False, include_plotlyjs='cdn')
