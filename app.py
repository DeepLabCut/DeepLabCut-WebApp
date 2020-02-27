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

fig.add_trace(go.Scatter(x=[], y=[], marker_color=[],
              marker_cmin=0, marker_cmax=3, mode='markers'))


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

options = ['nose', 'mouth', 'eye']
colors = px.colors.qualitative.Plotly

app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='basic-interactions',
            config={'editable':True},
            figure=fig,
    )],
    style={'width':'50%'}),
    html.Div([
        dcc.RadioItems(id='radio',
            options=[{'label':opt, 'value':opt} for opt in options],
            value=options[0]
        )], 
    style={'width':'40%'}),
    ])



@app.callback(
    [Output('basic-interactions', 'extendData'),
     Output('radio', 'value')],
    [Input('basic-interactions', 'clickData')],
    [State('radio', 'value')]
    )
def display_click_data(clickData, option):
    if clickData is None or fig is None:
        return dash.no_update, dash.no_update
    if clickData is None or fig is None:
        return dash.no_update
    x, y = clickData['points'][0]['x'], clickData['points'][0]['y']
    for i, el in enumerate(options):
        if el == option:
            new_option = options[(i+1)%(len(options))]
            color=i
    return [{'x':[[x]], 'y':[[y]], "marker.color":[[color]]}, [1]], new_option


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
