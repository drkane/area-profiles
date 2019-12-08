import json
import os
from collections import Counter
import random

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
# from dash.dependencies import Input, Output, State

from apps.utils import correct_titlecase
from .datapage import DataPage


class CompanyData(DataPage):

    subpage = 'companies'
    GPG_URL = 'https://gender-pay-gap.service.gov.uk/viewing/download-data/2018'
    size_order = [
        "Not Provided",
        "Less than 250",
        "250 to 499",
        "500 to 999",
        "1000 to 4999",
        "5000 to 19,999",
        "20,000 or more",
    ]

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

        data = [(k, c.get(k, 0)) for k in self.size_order if c.get(k, 0) > 0]

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
            'Number of companies by employer size'
        )

    def _largest_companies(self, c):

        largest_companies = {}
        count = 0
        limit_largest = 10
        for k in self.size_order[::-1]:
            top = [i for i in self.data if i["EmployerSize"] == k]
            if not top:
                continue
            largest_companies[k] = top
            count += len(largest_companies[k])
            if count > limit_largest:
                break

        list_items = []
        total_len = 0
        for k, v in largest_companies.items():
            original_len = len(v)
            len_left = limit_largest - total_len
            if len_left < 3:
                continue

            list_items.append(
                html.H4(className='f5', children='{} employees ({:,.0f})'.format(
                    k, original_len))
            )

            if original_len > len_left:
                v = random.sample(v, len_left)
                v = sorted(v, key=lambda x: x["EmployerName"])
                list_items.append(
                    html.P('* showing a random sample of {} companies'.format(len_left)))

            list_items.append(
                html.Ul(className='list pl0', children=[
                    html.Li(className='f6 mv1 lh-copy', children=[correct_titlecase(i["EmployerName"])]) for i in v
                ])
            )
            total_len += original_len

        return self.show_figure(
            html.Div(list_items),
            "Largest Companies"
        )


    def sidebar(self):

        c = Counter([c["EmployerSize"] for c in self.data])

        return [
            html.Div([
                html.Strong(className='f3 lh-copy pa0 ma0 header-font',
                            children="{:,.0f}".format(len(self.data))),
                html.Span(className='f5 lh-copy pa0 ma0',
                          children=' large companies')
            ]),
            self._size_table(c),
            self._largest_companies(c),
        ]

    def attribution(self):
        return dcc.Markdown('''
- Sourced from the [gender pay gap data](https://gender-pay-gap.service.gov.uk/) released by government
- Only includes companies with more than 250 employees (smaller companies are not required to report gender pay gap data)
- Company addresses are based on their registered office - for many companies most employees may be based outside of this area 
            ''')

    def map(self):
        return html.Figure(className='ma0 pa0 h-100', children=[
            # html.Figcaption('Map of companies'),
            html.Iframe(
                src=f'/map/{self.area["code"]}/companies',
                style={
                    'border': 0,
                    'width': '100%',
                    'height': '100%',
                }
            ),
        ])

    def map_params(self, request):
        return dict(
            markers={
                "Large companies": {
                    c["CompanyNumber"]: {
                        "lat": c["lat"],
                        "long": c["long"],
                        "name": c["EmployerName"],
                    } for c in self.data
                }
            },
        )


    @classmethod
    def import_data(cls, datadir=None):
        import pandas as pd
        import requests
        import requests_cache
        from tqdm import tqdm

        requests_cache.install_cache()

        pc_regex = r'([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})'
        pc_url = 'https://postcodes.findthatcharity.uk/postcodes/{}.json'

        print('fetching company data')
        df = pd.read_csv(cls.GPG_URL)
        df = df[df["CompanyNumber"].notnull()]
        df.loc[:, "Postcode"] = df["Address"].str.extract(pc_regex)[1]

        pc = {}
        print('fetch geodata for companies')
        for p in tqdm(df["Postcode"].unique()):
            if not isinstance(p, str):
                continue
            r = requests.get(pc_url.format(p.replace(" ", "")))
            try:
                r.raise_for_status()
                pc[p] = r.json().get("data", {}).get("attributes", {})
            except:
                continue

        df = df.join(
            pd.DataFrame(pc).T[
                ["lat", "long", "pcon", "cty", "laua", "ward", "lsoa11", "rgn"]
            ],
            on='Postcode'
        )

        if datadir is None:
            datadir = os.path.join(cls.datadir, cls.subpage)

        if not os.path.exists(datadir):
            os.mkdir(datadir)

        for i in df["pcon"].unique():
            filename = os.path.join(datadir, f'{i}.json')
            with open(filename, 'w') as a:
                df.loc[df["pcon"] == i, :].to_json(a, orient='records')
