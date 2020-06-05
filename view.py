import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import random
import uuid


class AppView:

    def __init__(self, name, db, config, server):
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        self.app = dash.Dash(name, external_stylesheets=external_stylesheets, server=server)
        self.db = db
        self.current_idx = 0
        self.appconfig = config
        self.pick_keypoint_subset()
        self.make_figure_image(self.current_idx)
        self.app.layout = self.make_layout()

    @property
    def options(self):
        return [self.appconfig.options[i] for i in self.subset]

    @property
    def fig(self):
        return self._fig

    def make_figure_image(self, i):
        data = self.db.fetch_image(i % len(self.db.dataset))
        fig = px.imshow(data.image)
        fig.layout.xaxis.showticklabels = False
        fig.layout.yaxis.showticklabels = False
        fig.update_traces(hoverinfo='none', hovertemplate='')
        fig.update_layout(
            title={
                'text': data.fname,
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'}
        )
        self._fig = fig
        return self._fig

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
                    config={
                        'editable': True,
                        'doubleClick': False,
                        'showTips': False,
                        'showLink': False,
                    },
                    figure=self.fig)
            ],
                className="six columns"
            ),
            html.Div([
                html.Div([
                    html.H3("DeepLabCut Labeling App"),
                    html.Div([
                        dcc.RadioItems(id='radio',
                                       options=[{'label': opt, 'value': opt} for opt in
                                                self.options],
                                       value=self.options[0]
                                       ),
                    ], style={"column-count": "4"}),
                ]),
                html.Div([
                    dcc.Input(
                        id="input_name",
                        type='text',
                        placeholder=str(uuid.uuid4()),
                    ),
                    html.Button('Previous', id='previous'),
                    html.Button('Next', id='next'),
                    html.Button('Clear', id='clear'),
                    html.Button('Save', id='save'),
                    dcc.Store(id='store', data=0),
                ]),
                html.Div([
                    html.Label('Keypoint label size'),
                    dcc.Slider(id='slider',
                               min=1,
                               max=24,
                               step=1,
                               value=8)
                ], style={'width': '80%',
                          'display': 'inline-block'})
            ],
                className="six columns"
            ),
            html.Div([
                dcc.Markdown("""
                        **Instructions**\n
                        Left click on the image to add a keypoint. Please skip/do not label occluded points. If you make a mistake, click clear to start again.

                        ![](/static/img/example_labels.png)
                    """),
                html.Pre(id='click-data', style=self.style['pre'])
            ],
                className='six columns',
                style={"overflow-x": "hidden"}
            ),
            html.Div(id='placeholder', style={'display': 'none'}),
            html.Div(id='shapes', style={'display': 'none'})
        ]
        )

    def pick_keypoint_subset(self):
        self.subset = list(range(len(self.appconfig.options)))
        #random.sample(range(len(self.appconfig.options)), self.appconfig.n2show)

    def refresh_radio_buttons(self):
        self.pick_keypoint_subset()
        return [{'label': opt, 'value': opt} for opt in self.options]
