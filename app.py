import flask

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import base64
import json
import os
import matplotlib.cm
import matplotlib.colors as mcolors
import numpy as np
import random
import plotly.graph_objects as go
import plotly.express as px
from skimage import data, transform, io
import numpy as np
import glob
import json

import view, model, config, utils

config = config.Config('config/config.json')
server = flask.Flask(__name__)
db = model.AppModel(config = config)
app = view.AppView(__name__, config = config, server = server, db = db)

COLORMAP = 'plasma'
cmap = matplotlib.cm.get_cmap(COLORMAP, len(config.options))

@app.callback(Output('placeholder', 'children'),
              [Input('save', 'n_clicks')],
              [State('store', 'data')])
def save_data(click_s, ind_image):
    if click_s:
        xy = {shape.name: utils.compute_circle_center(shape.path) for shape in app.fig.layout.shapes}
        print(xy, ind_image)

@app.callback(
    [Output('canvas', 'figure'),
     Output('radio', 'value'),
     Output('store', 'data'),
     Output('shapes', 'children')],
    [Input('canvas', 'clickData'),
     Input('canvas', 'relayoutData'),
     Input('next', 'n_clicks'),
     Input('previous', 'n_clicks'),
     Input('clear', 'n_clicks'),
     Input('slider', 'value')],
    [State('canvas', 'figure'),
     State('radio', 'value'),
     State('store', 'data'),
     State('shapes', 'children')]
    )
def update_image(clickData, relayoutData, click_n, click_p, click_c, slider_val,
                 figure, option, ind_image, shapes):

    print("Update Image")

    if not any(event for event in (clickData, click_n, click_p, click_c)):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    if ind_image is None:
        ind_image = 0

    if shapes is None:
        shapes = []
    else:
        shapes = json.loads(shapes)

    n_bpt = app.options.index(option)

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'slider':
        for i in range(len(shapes)):
            center = utils.compute_circle_center(shapes[i]['path'])
            new_path = utils.draw_circle(center, slider_val)
            shapes[i]['path'] = new_path
    else:
        if button_id == 'clear':
            app.fig.layout.shapes = []
        elif button_id == 'next':
            ind_image = (ind_image + 1) % len(db.dataset)
        elif button_id == 'previous':
            ind_image = (ind_image - 1) % len(db.dataset)
        print("request next image")
        return app.make_figure_image(ind_image), app.options[0], ind_image, '[]'


    already_labeled = [shape['name'] for shape in shapes]
    key = list(relayoutData)[0]
    if option not in already_labeled and button_id != 'slider':
        if clickData:
            x, y = clickData['points'][0]['x'], clickData['points'][0]['y']
            print(f"Added point {x},{y}")
            circle = utils.draw_circle((x, y), slider_val)
            color = utils.get_plotly_color(cmap, n_bpt)
            shape = dict(type='path',
                         path=circle,
                         line_color=color,
                         fillcolor=color,
                         layer='above',
                         opacity=0.8,
                         name=option)
            shapes.append(shape)
    else:
        if 'path' in key and button_id != 'slider':
            ind_moving = int(key.split('[')[1].split(']')[0])
            path = relayoutData.pop(key)
            shapes[ind_moving]['path'] = path

    app.fig.update_layout(shapes=shapes)
    if 'range[' in key:
        xrange = relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']
        yrange = relayoutData['yaxis.range[0]'], relayoutData['yaxis.range[1]']
        app.fig.update_xaxes(range=xrange, autorange=False)
        app.fig.update_yaxes(range=yrange, autorange=False)
    elif 'autorange' in key:
        app.fig.update_xaxes(autorange=True)
        app.fig.update_yaxes(autorange=True)
    if button_id != 'slider':
        n_bpt += 1
    new_option = app.options[min(len(app.options) - 1, n_bpt)]
    print("Show figure")
    return ({'data': figure['data'], 'layout': app.fig['layout']},
            new_option,
            ind_image,
            json.dumps(shapes))


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)