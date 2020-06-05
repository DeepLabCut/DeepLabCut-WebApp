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
import plotly.express as px
from skimage import data, transform

import utils, config, model, view


__version__ = "0.1"

print(f"| Starting version {__version__}")

config = config.Config('config/config.json')
db = model.AppModel(config = config)
cmap = matplotlib.cm.get_cmap('plasma', len(config.options))
server = flask.Flask(__name__)
view = view.AppView(__name__, db = db, config = config, server = server)


@server.route('/csv/')
def fetch_csv():
    return db.to_csv()

@server.route('/overview/')
def fetch_html():
    return db.to_html()

@view.app.callback(Output('placeholder', 'children'),
              [Input('save', 'n_clicks')],
              [State('store', 'data')])
def save_data(click_s, ind_image):
    if click_s:
        xy = {shape.name: utils.compute_circle_center(shape.path) for shape in view.fig.layout.shapes}
        print(xy, ind_image)

@view.app.callback(
    [Output('canvas', 'figure'),
     Output('radio', 'value'),
     Output('store', 'data'),
     Output('shapes', 'children'),
     ],
    [Input('canvas', 'clickData'),
     Input('canvas', 'relayoutData'),
     Input('next', 'n_clicks'),
     Input('previous', 'n_clicks'),
     Input('clear', 'n_clicks'),
     Input('slider', 'value'),
     Input('input_name', 'value')
     ],
    [State('canvas', 'figure'),
     State('radio', 'value'),
     State('store', 'data'),
     State('shapes', 'children')]
    )
def update_image(clickData, relayoutData, click_n, click_p, click_c, slider_val, username,
                 figure, option, ind_image, shapes):

    # TODO Refactor: Remove if/else statements and instead write multiple
    # callbacks.
    if not any(event for event in (clickData, click_n, click_p, click_c)):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    if ind_image is None: ind_image = 0
    shapes = [] if shapes is None else json.loads(shapes)
    n_bpt = view.options.index(option)

    ctx = dash.callback_context
    event = ctx.triggered[0]['prop_id']
    button_id = event.split('.')[0]
    if button_id == 'slider':
        for i in range(len(shapes)):
            center = utils.compute_circle_center(shapes[i]['path'])
            new_path = utils.draw_circle(center, slider_val)
            shapes[i]['path'] = new_path
    elif button_id in  ['clear', 'next', 'previous']:
        if button_id == 'clear':
            view.fig.layout.shapes = []
            view.fig.layout.xaxis.autorange = True
            view.fig.layout.yaxis.autorange = 'reversed'
        elif button_id == 'next':
            ind_image = (ind_image + 1) % len(db.dataset)
        elif button_id == 'previous':
            ind_image = (ind_image - 1) % len(db.dataset)
        return view.make_figure_image(ind_image), view.options[0], ind_image, '[]'

    already_labeled = [shape['name'] for shape in shapes]
    keys = list(relayoutData)
    key = keys[0] if len(keys) > 0 else ""
    if option not in already_labeled and button_id != 'slider' and 'relayout' not in event:
        if clickData:
            x, y = clickData['points'][0]['x'], clickData['points'][0]['y']
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
            db.add_annotation(
                name = option, username = username,
                xy = utils.compute_circle_center(circle)
            )
    else:
        if 'path' in key and button_id != 'slider':
            ind_moving = int(key.split('[')[1].split(']')[0])
            path = relayoutData.pop(key)
            shapes[ind_moving]['path'] = path
    view.fig.update_layout(shapes=shapes)
    
    if 'range[' in key and 'clickData' not in event:
        xrange = relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']
        yrange = sorted((relayoutData['yaxis.range[0]'], relayoutData['yaxis.range[1]']),
                        reverse=True)
        view.fig.update_xaxes(range=xrange, autorange=False)
        view.fig.update_yaxes(range=yrange, autorange=False)
    elif 'autorange' in key:
        view.fig.update_xaxes(autorange=True)
        view.fig.update_yaxes(autorange='reversed')
    if button_id != 'slider' and 'relayout' not in event:
        n_bpt += 1
    new_option = view.options[min(len(view.options) - 1, n_bpt)]
    return ({'data': figure['data'], 'layout': view.fig['layout']},
            new_option,
            ind_image,
            json.dumps(shapes))


if __name__ == '__main__':
    view.app.run_server(debug=False, port=8051)
