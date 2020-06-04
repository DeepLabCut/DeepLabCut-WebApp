import flask

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas
import plotly.graph_objects as go
import plotly.express as px
from skimage import data, transform
import numpy as np

import json

def load_image(url):
    print(f"Loading {url}")
    from PIL import Image
    import requests
    from io import BytesIO

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return np.array(img)

class AppContext():

    def __init__(self, app, config = "config/config.json"):

        self.app = app
        self.load_config(config)

        # example data
        img = data.chelsea()
        img = img[::2, ::2]
        #self.images = [img, img[::-1], transform.rotate(img, 30)]
        self.select_image(0)

    def make_figure_image(self, i):
        img = load_image(self.fnames[i % len(self.fnames)])
        fig = px.imshow(img)
        fig.update_traces(hoverinfo='none')
        fig.add_trace(go.Scatter(x=[], y=[], marker_color=[],
                    marker_cmin=0, marker_cmax=3, marker_size=18, mode='markers'))
        return fig

    def load_config(self, config):
        with open(config, "r") as fp:
            self.config = json.load(fp)
        with open(self.config["urls"], "r") as fp:
            self.fnames = [f for f in fp.read().split('\n') if len(f)]

    def select_image(self, i):
        self._fig = self.make_figure_image(i)
        return self.fig

    @property
    def fig(self):
        return self._fig

    @property
    def options(self):
        return self.config["options"]

    def create_layout(self):
        self.app.layout = html.Div([
            html.Div([
                dcc.Graph(
                    id='basic-interactions',
                    config={'editable':True},
                    figure=self.fig,
            )],
            className="six columns"
            ),
            html.Div([
                html.H2("Controls"),
                dcc.RadioItems(id='radio',
                    options=[{'label':opt, 'value':opt} for opt in self.options],
                    value=self.options[0]
                ),
                html.Button('Previous', id='previous'),
                html.Button('Next', id='next'),
                dcc.Store(id='store', data=0)
                ], 
            className="six columns"
            ),
            ])
        return self

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server = server)
context = AppContext(app).create_layout()

@app.callback(
    [Output('basic-interactions', 'figure'),
     Output('store', 'data')],
    [Input('next', 'n_clicks'),
     Input('previous', 'n_clicks')],
    [State('store', 'data')]
    )
def display_click_data(n_clicks_n, n_clicks_p, val):
    if n_clicks_n is None and n_clicks_p is None:
        return dash.no_update, dash.no_update
    if val is None:
        val = 0
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    index = val + 1 if button_id == 'next' else val - 1
    fig = context.select_image(index)
    return fig, index


@app.callback(
    [Output('basic-interactions', 'extendData'),
     Output('radio', 'value')],
    [Input('basic-interactions', 'clickData')],
    [State('radio', 'value')]
    )
def display_click_data(clickData, option):
    print(context)
    if clickData is None or context.fig is None:
        return dash.no_update, dash.no_update
    if clickData is None or context.fig is None:
        return dash.no_update
    x, y = clickData['points'][0]['x'], clickData['points'][0]['y']
    for i, el in enumerate(context.options):
        if el == option:
            new_option = context.options[(i+1)%(len(context.options))]
            color=i
    return [{'x':[[x]], 'y':[[y]], "marker.color":[[color]]}, [1]], new_option


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)