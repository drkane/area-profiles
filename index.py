import re

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import area, area_select


app.layout = html.Div(id='container', className='home w-100 sans-serif near-black base-font bg-wavy h-100', children=[
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', className='h-100 flex flex-column'),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    path_match = r'^\/(?P<page_type>area|pcon|la)(\/(?P<area_code>[A-Za-z0-9]+)(\/(?P<sub_page>[A-Za-z0-9]+))?)?\/?$'
    if not isinstance(pathname, str):
        return '404'

    if pathname is None:
        return area_select.layout

    path_vars = re.search(path_match, pathname)

    if path_vars is None:
        return area_select.layout
    
    path_vars = path_vars.groupdict()
    page_type = path_vars.get('page_type')
    area_code = path_vars.get('area_code')
    sub_page = path_vars.get('sub_page')

    if not area_code:
        return area_select.layout

    return area.layout(area_code, sub_page)


if __name__ == '__main__':
    app.run_server(debug=True)
