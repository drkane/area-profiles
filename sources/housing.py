import json
import os
import io
from collections import defaultdict
import random

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
# from dash.dependencies import Input, Output, State
from tqdm import tqdm
import requests

from apps.utils import correct_titlecase
from .datapage import DataPage


class HousingData(DataPage):

    subpage = 'housing'
    PRICE_PAID_URL = 'https://www.ons.gov.uk/file?uri=%2fpeoplepopulationandcommunity%2fhousing%2fdatasets%2fmedianpricepaidbylowerlayersuperoutputareahpssadataset46%2fcurrent/hpssadataset46medianpricepaidforresidentialpropertiesbylsoa.xls'
    size_order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def __init__(self, area, filters=None, datadir='./data'):
        self.area = area
        self.filters = filters
        self.datadir = datadir
        self.data = self._fetch_data()

    def _fetch_data(self):
        f = os.path.join(self.datadir, self.subpage, f"{self.area['code']}.json")
        if os.path.exists(f):
            with open(f) as a:
                return json.load(a)
        return None

    def _size_table(self, c):

        data = [(k, c.get(k, 0)) for k in self.size_order]

        colours = [
            "#0864A7",
            "#0978C7",
            "#2690CC",
            "#4AADD2",
            "#7DCBD8",
            "#B0E1D6",
            "#D3EED5",
            "#E3F5D8",
            "#EFFCCA",
            "#FBFCB9",
        ]

        total = sum([i[1] for i in data])

        return self.show_figure(
            html.Div([
                dcc.Markdown(className='f6', children='''
Each bar shows the proportion of people living in LSOAs in each national deprivation decile.
'''),
                html.Div(className='f7', children='Least deprived'),
                dcc.Graph(
                    figure=go.Figure(
                        data=[
                            go.Bar(
                                x=[i[1] / total for i in data],
                                y=[i[0] for i in data],
                                text=[
                                    "{:,.1%}".format(
                                        i[1] / total,
                                        # " people" if i[0] == 10 else ""
                                    )
                                    for i in data
                                ],
                                textposition='auto',
                                orientation='h',
                                hoverinfo='none',
                                marker=dict(
                                    color=colours
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
                html.Div(className='f7', children='Most deprived'),
            ]),
            'Levels of deprivation'
        )


    def sidebar(self):

        if not self.data:
            return []

        c = defaultdict(int)
        for i in self.data.values():
            c[i["Index of Multiple Deprivation (IMD) Decile (where 1 is most deprived 10% of LSOAs)"]
              ] += i["Total population: mid 2015 (excluding prisoners)"]

        return [
            self._size_table(c),
        ]

    def map(self):
        return html.Figure(className='ma0 pa0 h-100', children=[
            # html.Figcaption('Map of companies'),
            html.Iframe(
                src=f'/map/{self.area["code"]}/deprivation',
                style={
                    'border': 0,
                    'width': '100%',
                    'height': '100%',
                }
            ),
        ])

    def map_params(self, request):
        if self.data:
            return dict(
                lsoa_fill={
                    "IMD 2019": {
                        "data": {
                            k: i["Index of Multiple Deprivation (IMD) Decile (where 1 is most deprived 10% of LSOAs)"]
                            for k, i in self.data.items()
                        },
                        "onByDefault": True,
                    }
                }
            )
        return {}

    def attribution(self):
        return dcc.Markdown('''
- the [Index of Multiple Deprivation](https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019) published by MHCLG

The colours on the map indicate the deprivation decile of each Lower Layer Super Output Area (LSOA)
for England as a whole, and the coloured bars indicate the number of people living in LSOAs in each national
deprivation decile. The most deprived areas (decile 1) are shown in blue.

It is important to keep in mind that the Indices of Deprivation relate to small areas and do not tell us
how deprived, or wealthy, individual people area. LSOAs have an average population of just under 1,700 (as of 2017).
            ''')


    @classmethod
    def import_data(cls, datadir=None):
        import pandas as pd

        r = requests.get(cls.PRICE_PAID_URL)
        df = pd.read_excel(io.BytesIO(r.content), skiprows=5, sheet_name='Data', index_col="LSOA code")

        if datadir is None:
            datadir = cls.datadir

        datadir = os.path.join(datadir, cls.subpage)

        if not os.path.exists(datadir):
            os.mkdir(datadir)

        for i in tqdm(os.listdir(os.path.join(cls.datadir, 'boundaries'))):
            if not i.endswith("_lsoa.geojson"):
                continue

            with open(os.path.join(cls.datadir, 'boundaries', i)) as a:
                b = json.load(a)
                lsoas = [i["properties"]["code"] for i in b["features"]]
                pcon = i.replace("_lsoa.geojson", "").split("/")[-1]
                filename = os.path.join(datadir, f'{pcon}.json')
                with open(filename, 'w') as a:
                    df.loc[df.index.isin(lsoas), :].to_json(a, orient='index')
