import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import base64
import os
import random
import plotly.graph_objects as go
import plotly.express as px
from skimage import data, transform


KEYPOINTS = ['Nose', 'L_Eye', 'R_Eye', 'L_Ear', 'R_Ear', 'Throat',
             'Withers', 'TailSet', 'L_F_Paw', 'R_F_Paw', 'L_F_Wrist',
             'R_F_Wrist', 'L_F_Elbow', 'R_F_Elbow', 'L_B_Paw', 'R_B_Paw',
             'L_B_Hock', 'R_B_Hock', 'L_B_Stiffle', 'R_B_Stiffle']
IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'full_dog.png')


img = data.chelsea()
img = img[::2, ::2]
images = [img, img[::-1], transform.rotate(img, 30)]
encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read())


def make_figure_image(i):
    fig = px.imshow(images[i % len(images)])
    fig.layout.xaxis.showticklabels = False
    fig.layout.yaxis.showticklabels = False
    fig.update_traces(hoverinfo='none', hovertemplate='')
    fig.add_trace(go.Scatter(x=[], y=[], marker_color=[], text=[],
                             marker_cmin=0, marker_cmax=3, marker_size=18, mode='markers'))
    return fig


fig = make_figure_image(0)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

options = random.sample(KEYPOINTS, 3)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='basic-interactions',
            config={'editable': False},
            figure=fig)
    ],
        className="six columns"
    ),
    html.Div([
        html.H2("Controls"),
        dcc.RadioItems(id='radio',
                       options=[{'label':opt, 'value':opt} for opt in options],
                       value=options[0]
                       ),
        html.Button('Previous', id='previous'),
        html.Button('Next', id='next'),
        html.Button('Clear', id='clear'),
        dcc.Store(id='store', data=0)
    ],
        className="six columns"
    ),
    html.Div([
        dcc.Markdown("""
                **Instructions**\n
                Click on the image to add a keypoint.
            """),
        html.Pre(id='click-data', style=styles['pre']),
        # html.Img(src='data:image/png;charset=utf-8;base64,{}'.format(encoded_image))
    ],
        className='six columns'
    ),
    html.Div(id='already-labeled', style={'display': 'none'})
]
)


@app.callback(
    [Output('basic-interactions', 'figure'),
     Output('radio', 'value'),
     Output('store', 'data')],
    [Input('basic-interactions', 'clickData'),
     Input('next', 'n_clicks'),
     Input('previous', 'n_clicks'),
     Input('clear', 'n_clicks')],
    [State('basic-interactions', 'figure'),
     State('radio', 'value'),
     State('store', 'data')]
    )
def update_image(clickData, click_n, click_p, click_c, figure, option, ind_image):
    if not any(event for event in (clickData, click_n, click_p, click_c)):
        return dash.no_update, dash.no_update, dash.no_update

    if ind_image is None:
        ind_image = 0

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'clear':
        fig = make_figure_image(ind_image)
        return fig, options[0], ind_image
    elif button_id == 'next':
        ind_image += 1
        fig = make_figure_image(ind_image)
        return fig, options[0], ind_image
    elif button_id == 'previous':
        ind_image -= 1
        fig = make_figure_image(ind_image)
        return fig, options[0], ind_image

    n_bpt = options.index(option)
    x, y = clickData['points'][0]['x'], clickData['points'][0]['y']
    data = figure['data'][1]
    if n_bpt >= len(data['x']):
        data['x'].append(x)
        data['y'].append(y)
        data['text'].append(option)
        data['marker']['color'].append(n_bpt)
    else:
        data['x'][n_bpt] = x
        data['y'][n_bpt] = y
    new_option = options[min(len(options) - 1, n_bpt + 1)]
    return figure, new_option, ind_image


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
