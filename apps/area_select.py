import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

from app import app
from .data import fetch_areas

areas = fetch_areas()

layout = [
    html.Header(id='area-header',
                className="body header-font ph3 ph3-ns pt3 pt3-ns pb3 moon-gray cf center mw9 w-100",
                children=[
                    html.Iframe(
                        src=f'/map/locator/dgsdg',
                        className='fr',
                        style={
                            'border': 0,
                            'width': '120px',
                            # 'height': '100',
                        }
                    ),
                    html.H2(className='f1-ns f1 lh-solid mv0 logo', children=[
                        html.A(className='link moon-gray underline-yellow underline',
                               children='Constituency profiles'),
                    ]),
                    html.H3(className='f3-ns f3 lh-solid mv3', children=['Select an area']),
                ]),
    html.Div(className='bg-white h-100', children=[
        html.Div(className='w-100 mw7-ns pa2 flex-auto center', children=[
            html.H1(className='f3 lh-solid mv3 header-font', children='Parliamentary constituencies'),
            dcc.Dropdown(
                id='area-selection',
                options=[
                    {"label": f"{a['name']} ({a['type']})", "value": a["code"]}
                    for a in areas
                ]
            ),
            html.H1(className='f3 lh-solid mb3 mt5 header-font',
                    children='About this tool'),
            dcc.Markdown(className='entry-content', children='''
This tool brings together data from a variety of sources to 
create a profile of local areas.
It was inspired by [Alasdair Rae's Constituency Cards](https://github.com/alasdairrae/wpc/), and uses some of the same data.

For each area you can view information about:

- the results and candidates for the 2017 & 2019 general elections
- levels of deprivation
- local charities
- local large businesses with headquarters in the area

The tool is made by [David Kane](https://dkane.net) and it's a work in progress - I hope to add areas, more data sources and keep refining the site.

I've used Plotly's [Dash](https://dash.plot.ly/) and the maps are powered by [Leaflet](https://leafletjs.com/).

## Data sources

Data is used under open licences from a variety of places:

### Election data

- constituency data from [Alasdair Rae](https://github.com/alasdairrae/wpc/), which is sourced from a number of places
  including the Parliamentary Digital Service, House of Commons Library and mysociety & Democracy Club.
- candidates for the 2019 election are sourced from Democracy Club's amazing effort to [source open election data](https://candidates.democracyclub.org.uk/).

### Deprivation data

- the [Index of Multiple Deprivation](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019) published by MHCLG

### Charities data

- from the [Charity Commission](https://beta.charitycommission.gov.uk/), [OSCR](https://www.oscr.org.uk/) 
  and [CCNI](https://www.charitycommissionni.org.uk/). 
- Also includes [some of my own data](https://github.com/drkane/charity-lookups) on charities.

### Companies data

- sourced from the [gender pay gap data](https://gender-pay-gap.service.gov.uk/) released by government

### Boundaries and geodata

- geodata and boundaries are sourced from [ONS Geoportal](http://geoportal.statistics.gov.uk/)
- Source: Office for National Statistics licensed under the Open Government Licence v.3.0
- Contains OS data © Crown copyright and database right 2019
- Map data for backgrounds is © OpenStreetMap contributors and imagery is created by mapbox


Unless otherwise stated data is used under the Open Government Licence.
            '''),
        ]),
    ]),
]


@app.callback([Output('url', 'pathname')],
              [Input('area-selection', 'value')])
def change_url(area_select):
    return (f'/area/{area_select}', )
