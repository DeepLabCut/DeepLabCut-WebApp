import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import random
import plotly.graph_objects as go
import plotly.express as px
from skimage import data, transform


KEYPOINTS = ['Nose', 'L_Eye', 'R_Eye', 'L_Ear', 'R_Ear', 'Throat',
             'Withers', 'TailSet', 'L_F_Paw', 'R_F_Paw', 'L_F_Wrist',
             'R_F_Wrist', 'L_F_Elbow', 'R_F_Elbow', 'L_B_Paw', 'R_B_Paw',
             'L_B_Hock', 'R_B_Hock', 'L_B_Stiffle', 'R_B_Stiffle']

img = data.chelsea()
img = img[::2, ::2]
images = [img, img[::-1], transform.rotate(img, 30)]


def make_figure_image(i):
    fig = px.imshow(images[i % len(images)])
    fig.update_traces(hoverinfo='none', hovertemplate='')
    fig.add_trace(go.Scatter(x=[], y=[], marker_color=[],
                             marker_cmin=0, marker_cmax=3, marker_size=18, mode='markers'))
    return fig


fig = make_figure_image(0)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

options = random.sample(KEYPOINTS, 3)
already_labeled = set()


app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='basic-interactions',
            config={'editable':True},
            figure=fig,
    )],
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
    ])


@app.callback(
    [Output('basic-interactions', 'figure'),
     Output('store', 'data')],
    [Input('next', 'n_clicks'),
     Input('previous', 'n_clicks'),
     Input('clear', 'n_clicks')],
    [State('store', 'data')]
    )
def display_click_data(n_clicks_n, n_clicks_p, n_clicks_c, val):
    if not any(click for click in (n_clicks_n, n_clicks_p, n_clicks_c)):
        return dash.no_update, dash.no_update
    if val is None:
        val = 0
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'clear':
        fig = make_figure_image(val)
        global already_labeled
        already_labeled = set()
        # app.layout.children[1].children[1].value = options[0]
        return fig, val
    index = val + 1 if button_id == 'next' else val - 1
    fig = make_figure_image(index)
    return fig, index


@app.callback(
    [Output('basic-interactions', 'extendData'),
     Output('radio', 'value')],
    [Input('basic-interactions', 'clickData')],
    [State('radio', 'value')]
    )
def display_click_data(clickData, option):
    if clickData is None or fig is None:
        return dash.no_update, dash.no_update
    n_bpt = options.index(option)
    if n_bpt in already_labeled:
        return dash.no_update, dash.no_update
    already_labeled.add(n_bpt)
    x, y = clickData['points'][0]['x'], clickData['points'][0]['y']
    new_option = options[min(len(options) - 1, n_bpt + 1)]
    return [{'x':[[x]], 'y':[[y]], "marker.color":[[n_bpt]]}, [1]], new_option


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
