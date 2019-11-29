import json
import os
from collections import defaultdict
import random

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
# from dash.dependencies import Input, Output, State
from tqdm import tqdm

from .datapage import DataPage
from apps.utils import correct_titlecase


class DeprivationData(DataPage):

    subpage = 'deprivation'
    IMD_2019_URL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/845345/File_7_-_All_IoD2019_Scores__Ranks__Deciles_and_Population_Denominators_3.csv'
    size_order = [1,2,3,4,5,6,7,8,9,10]

    def __init__(self, area, filters=None):
        self.area = area
        self.filters = filters
        self.data = self._fetch_data()


    def _fetch_data(self):
        f = f"./data/deprivation/{self.area['code']}.json"
        if os.path.exists(f):
            with open(f) as a:
                return json.load(a)
        return None

    def _size_table(self, c):

        data = [(k, c.get(k, 0)) for k in self.size_order]

        colours = [
            "#0D8000",
            "#27830F",
            "#42871E",
            "#5D8B2D",
            "#788F3C",
            "#93934B",
            "#AE975A",
            "#C99B69",
            "#E49F78",
            "#FFA388",
        ]

        return self.show_figure(
            html.Div([
                html.Div(className='f7', children='Least deprived'),
                dcc.Graph(
                    figure=go.Figure(
                        data=[
                            go.Bar(
                                x=[i[1] for i in data],
                                y=[i[0] for i in data],
                                text=[
                                    "{:,.0f}{}".format(
                                        i[1],
                                        " people" if i[0] == 10 else ""
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
            'Population by levels of deprivation'
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


    @classmethod
    def import_data(cls, datadir=None):
        import pandas as pd

        df = pd.read_csv(cls.IMD_2019_URL, index_col="LSOA code (2011)")

        if datadir is None:
            datadir = os.path.join(cls.datadir, cls.subpage)

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
