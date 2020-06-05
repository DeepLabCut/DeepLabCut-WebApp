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

class AppView(dash.Dash):

    def __init__(self, name, server, db, config):
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        super().__init__(name, external_stylesheets=external_stylesheets, server = server)
        self.db = db
        self.current_idx = 0
        self.appconfig = config
        self.make_figure_image()
        self.layout = self.make_layout()


    @property
    def fig(self):
        print("Requested figure")
        return self._fig

    @property
    def options(self):
        return self.appconfig.options

    def make_figure_image(self, index = None):
        if index is not None:
            self.current_idx = index

        print("Fetch data")
        
        data = self.db.fetch_image(self.current_idx)
        fig = px.imshow(data.image)
        fig.layout.xaxis.showticklabels = False
        fig.layout.yaxis.showticklabels = False
        fig.update_traces(hoverinfo='none')
        #fig.add_trace(go.Scatter(x=[], y=[], marker_color=[],
        #            marker_cmin=0, marker_cmax=3, marker_size=18, mode='markers'))
        fig.update_layout(
            title={
                'text': data.fname,
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'}
        )
        print("Rendered Figure.")
        self._fig = fig
        return self.fig

    @property
    def style(self):
        return {
            'pre': {
                'border': 'thin lightgrey solid',
                'overflowX': 'scroll'
            }
        }

    def make_layout(self):
        return html.Div([
            html.Div([
                dcc.Graph(
                    id='canvas',
                    config={'editable': True},
                    figure=self.fig)
            ],
                className="six columns"
            ),
            html.Div([
                html.H2("Controls"),
                dcc.RadioItems(id='radio',
                            options=[{'label': opt, 'value': opt} for opt in self.options],
                            value=self.options[0]
                            ),
                html.Button('Previous', id='previous'),
                html.Button('Next', id='next'),
                html.Button('Clear', id='clear'),
                html.Button('Save', id='save'),
                dcc.Store(id='store', data=0),
                html.P([
                    html.Label('Keypoint size'),
                    dcc.Slider(id='slider',
                            min=3,
                            max=36,
                            step=1,
                            value=12)
                    ], style={'width': '80%',
                            'display': 'inline-block'})
            ],
                className="six columns"
            ),
            html.Div([
                dcc.Markdown("""
                        **Instructions**\n
                        Click on the image to add a keypoint.
                    """),
                html.Pre(id='click-data', style=self.style['pre'])
            ],
                className='six columns'
            ),
            html.Div(id='placeholder', style={'display': 'none'}),
            html.Div(id='shapes', style={'display': 'none'})
        ]
        )