import dash_core_components as dcc
import dash_html_components as html
# import plotly.graph_objs as go
from dash.dependencies import Input, Output #, State

from app import app
from sources import get_source_cls
from .data import fetch_area


def layout(area_code, subpage=None):

    area = fetch_area(area_code)

    return [
        html.Header(id='area-header',
                    className="body header-font ph3 ph3-ns pt3 pt3-ns pb3 moon-gray cf center mw9 w-100"),
        html.Div(className='bg-white h-100', children=[
            html.Div(className='flex h-100 ph0 center mw9 w-100 cf', children=[
                dcc.Store(id='area', data=area),
                dcc.Store(id='subpage', data=subpage),
                html.Div(className='fl w-100 w-third-ns pa2', children=[
                    html.Div(id='main-display'),
                    html.Div(className='bg-light-gray pa2', children=[
                        html.H3(className='mv2 pa0 f4 header-font b', children='Data sources'),
                        html.Div(id='attribution'),
                    ]),
                ]),
                html.Div(className='fl w-100 w-two-thirds-ns pa2 flex-auto', children=[
                    html.Div(id='map-display', className='h-100')
                ]),
            ]),
        ]),
    ]



@app.callback(
    [Output('area-header', 'children'),
     Output('main-display', 'children'),
     Output('map-display', 'children'),
     Output('attribution', 'children'),],
    [Input('area', 'data'),
     Input('subpage', 'data')])
def display_value(area, subpage):

    data = get_source_cls(subpage, area['type'])(area)

    return (
        data.header(),
        data.sidebar(),
        data.map(),
        [
            data.attribution(),
            data.boundary_attribution(),
        ]
    )
