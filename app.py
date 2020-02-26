import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import plotly.express as px
from skimage import data, transform

img = data.chelsea()
img = img[::2, ::2]
fig = px.imshow(img)

fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers'))


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    dcc.Graph(
        id='basic-interactions',
        config={'editable':True},
        figure=fig,
    ),

])



@app.callback(
    Output('basic-interactions', 'extendData'),
    [Input('basic-interactions', 'clickData')],
    [State('basic-interactions', 'figure')],
    )
def display_click_data(clickData, fig):
    if clickData is None or fig is None:
        return dash.no_update
    if clickData is None or fig is None:
        return dash.no_update
    x, y = clickData['points'][0]['x'], clickData['points'][0]['y']
    return [dict(x=[[x]], y=[[y]]), [1]]


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
