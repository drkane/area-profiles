import os
import json

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


class DataPage:

    subpage = ''
    areatype_names = {
        'pcon': 'Parliamentary Constituency',
        'la': 'Local Authority',
        'la_upper': 'Local Authority',
        'la_lower': 'Local Authority',
    }
    datadir = 'data'

    def __init__(self, area, filters=None, datadir='./data'):
        self.area = area
        self.filters = filters
        self.data = self._fetch_data()
        self.datadir = datadir

    def _fetch_data(self):
        f = os.path.join(self.datadir, f"election/{self.area['code']}.json")
        if os.path.exists(f):
            with open(f) as a:
                return json.load(a)
        return None


    def header(self):
        return [
            html.Iframe(
                src=f'/map/locator/{self.area["code"]}',
                className='fr',
                style={
                    'border': 0,
                    'width': '120px',
                    # 'height': '100',
                }
            ),
            html.H2(className='f1-ns f1 lh-solid mv0 logo', children=[
                html.A(className='link moon-gray underline-yellow underline', children=self.area["name"]),
            ]),
            html.H3(className='f3-ns f3 lh-solid mv3', children=[
                self.areatype_names.get(self.area["type"], self.area["type"]),
                " | ",
                self.area["code"],
            ]),
            html.P(className='pa0 mb0 mt5 f5 lh-copy', children=[
                dcc.Link(className='pa0 ma0 yellow link dim underline', href='/area/', children=[
                    "< Select another area"
                ]),
                " | ",
                html.Span(className='pa0 ma0', children=[
                    "Explore this area: "
                ]),
                dcc.Link(
                    className='b pa0 ma0 yellow link dim underline',
                    href=f'/area/{self.area["code"]}',
                    children="Home",
                ),
                " · ",
                dcc.Link(
                    className='b pa0 ma0 yellow link dim underline',
                    href=f'/area/{self.area["code"]}/elections',
                    children="Election",
                ),
                " · ",
                dcc.Link(
                    className='b pa0 ma0 yellow link dim underline',
                    href=f'/area/{self.area["code"]}/deprivation',
                    children="Deprivation",
                ),
                " · ",
                dcc.Link(
                    className='b pa0 ma0 yellow link dim underline',
                    href=f'/area/{self.area["code"]}/charities',
                    children="Charities",
                ),
                " · ",
                dcc.Link(
                    className='b pa0 ma0 yellow link dim underline',
                    href=f'/area/{self.area["code"]}/companies',
                    children="Companies",
                ),
            ]),
        ]

    def _population_chart(self):

        data = [
            ("65+", self.data.get("65_plus_17")),
            ("16-65", self.data.get("16_64_2017")),
            ("Under 16", self.data.get("0_15_2017")),
        ]

        return self.show_figure(
            dcc.Graph(
                figure=go.Figure(
                    data=[
                        go.Bar(
                            x=[i[1] for i in data],
                            y=[i[0] for i in data],
                            text=["{} ({:,.0f})".format(*i) for i in data],
                            textposition='auto',
                            orientation='h',
                            hoverinfo='none',
                            marker=dict(
                                color='#0D8000'
                            ),
                        )
                    ],
                    layout=go.Layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        margin=go.layout.Margin(l=0, r=0, t=0, b=0),
                        xaxis=dict(
                            visible=False,
                            rangemode='tozero',
                            showgrid=False,
                        ),
                        yaxis=dict(
                            visible=False,
                            showgrid=False,
                            automargin=True,
                        ),
                    ),
                ),
                config=dict(
                    displayModeBar=False,
                ),
                style={'height': 30 * len(data), 'width': '100%'},
                id='vote-at-previous',
            ),
            'Local population'
        )


    def sidebar(self):
        return [
            dcc.Markdown(f'''
**{self.area["name"]}** is a {self.areatype_names.get(self.area["type"], self.area["type"])} located in {self.data.get('ukpart')}.
It has a population of {self.data.get("pop17"):,.0f} across an area of {self.data.get("sq_mi"):,.0f} square miles.
            '''),
            self._population_chart(),
            # html.Pre(json.dumps(self.data, indent=4))
        ]

    def map(self):
        return html.Figure(className='ma0 pa0 h-100', children=[
            # html.Figcaption('Map of charities'),
            html.Iframe(
                src=f'/map/{self.area["code"]}',
                style={
                    'border': 0,
                    'width': '100%',
                    'height': '100%',
                }
            ),
        ])

    def map_params(self, request):
        return dict()

    def attribution(self):
        return dcc.Markdown()

    def boundary_attribution(self):
        return dcc.Markdown('''
### Boundary data

- Source: Office for National Statistics licensed under the Open Government Licence v.3.0
- Contains OS data © Crown copyright and database right 2019

© 2019 [David Kane](https://dkane.net)
        ''')

    @staticmethod
    def show_figure(children, caption=None):
        if not isinstance(children, list):
            children = [children]
        if caption:
            children = [
                html.Figcaption(
                    className='mv2 pa0 f4 header-font b', children=caption)
            ] + children
        return html.Figure(className='mh0 mv4 pa0', children=children)

    @classmethod
    def import_data(cls, datadir=None):
        pass
