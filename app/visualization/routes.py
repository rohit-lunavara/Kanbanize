from dash import Dash
import dash_html_components as html
import dash_core_components as dcc
from flask_login import login_required

def dash_app() :
    # Create a Dash app
    dash_app = Dash(
        __name__,
        server = False,
        url_base_pathname = "/visualization/"
    )

    dash_app.layout = html.Div([
    html.H1('Dash application'),
    dcc.Graph(
        id='basic-graph',
        figure={
            'data':[
                {
                    'x': [0, 1],
                    'y': [0, 1],
                    'type': 'line'
                }
            ],
            'layout': {
                'title': 'Basic Graph'
            }
        }
    )])

    return dash_app