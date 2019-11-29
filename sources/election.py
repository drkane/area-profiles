import json
import os

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
# from dash.dependencies import Input, Output, State

from .datapage import DataPage


class ElectionData(DataPage):

    subpage = 'election'
    WPC_URL = 'https://raw.githubusercontent.com/alasdairrae/wpc/master/files/wpc_2019_flat_file_v9.csv'
    DEMOCLUB_URL = 'https://candidates.democracyclub.org.uk/media/candidates-parl.2019-12-12.csv'

    def __init__(self, area, filters=None):
        self.area = area
        self.filters = filters
        self.data = self._fetch_data()


    def _fetch_data(self):
        f = f"./data/election/{self.area['code']}.json"
        if os.path.exists(f):
            with open(f) as a:
                return json.load(a)
        return None

    def _make_chart(self):
        parties = {
            "con": ("Conservative", "#0575c9"),
            "lab": ("Labour", "#ed1e0e"),
            "ld": ("Liberal Democrat", "#fe8300"),
            "ukip": ("Ukip", '#6e2c76'),
            "green": ("Green", "#78c31e"),
            "snp": ("SNP", "#ebc31c"),
            "pc": ("Plaid Cymru", "#4e9f2f"),
            "dup": ("DUP", "#c0153d"),
            "sf": ("Sinn Féin", "#00623f"),
            "sdlp": ("SDLP", "#006e50"),
            "uup": ("UUP", "#48a5ee"),
            "alliance": ("Alliance", "#f6cb2f"),
            "other": ("Others", "#f3a6b2"),
            "independent": ("Independent", "#f3a6b2"),
            "nha": ("National Health Action", "#176da6"),
            "bp": ("The Brexit Party", "#03b6d0"),
            "spk": ("Speaker", "#076796"),
        }
        results = [
            (*parties.get(k), self.data.get(k), k)
            for k in parties
            if self.data.get(k, 0) > 0
        ]
        results = sorted(results, key=lambda x: x[2])

        if results[-1][3] == "other":
            other = results[-1]
            results[-1] = (self.data['partydisp'],
                           self.data['partycol'],
                           self.data['VOTES1'],
                           self.data['partydisp'].lower())
            other = (
                other[0],
                other[1],
                (other[2] - self.data['VOTES1']),
                other[3]
            )
            if other[2] > 0:
                results.append(other)
                results = sorted(results, key=lambda x: x[2])

        return dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=[i[2] for i in results],
                        y=[i[0] for i in results],
                        text=["{}<br>{:,.0f}".format(i[0], i[2]) for i in results],
                        textposition='auto',
                        orientation='h',
                        marker=dict(
                            color=[i[1] for i in results]
                        ),
                        hoverinfo='none',
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
            style={'height': 50 * len(results), 'width': '100%'},
            id='vote-at-previous',
        )

    def _candidates_list(self):

        return self.show_figure(
            html.Ul(className='list pl0', children=[
                html.Li(
                    className='f6 mv1 lh-copy cf pa2 bg-light-gray near-black',
                    children=[
                        html.Img(className='w3 fr person-photo',
                                 src=c["image_url"]) if c["image_url"] else None,
                        html.Span(className='f5 b', children=c["name"]),
                        html.Br(),
                        html.Span(className='f6', children=c["party_name"]),
                    ]
                )
                for c in self.data.get("candidates", [])
            ]),
            'Candidates for 2019 Election'
        )


    def sidebar(self):
        return [
            html.Div(
                className='pa2 cf',
                style={
                    'backgroundColor': self.data['partycol'],
                    'color': '#fff',
                },
                children=[
                    html.Img(className='fr w3 person-photo', src=self.data['photo_url']),
                    html.P(className='pa0 ma0', children='Current MP'),
                    html.P(className='pa0 ma0', children=[
                        html.Strong(className='f3 lh-copy pa0 ma0 calistoga',
                                    children=self.data['dispname']),
                        html.Span(' ({})'.format(self.data['partydisp']))
                    ]),
                    html.P(className='pa0 ma0 f6', children=[
                        'Elected {}. Majority {:,.0f}.'.format(
                            self.data["last_vote"],
                            self.data['majority'],
                        )
                    ]),
                ]
            ),
            self.show_figure(
                self._make_chart(),
                "Result of 2017 election"
            ),
            self._candidates_list(),
        ]

    def map(self):
        return html.Figure(className='ma0 pa0 h-100', children=[
            # html.Figcaption('Map of charities'),
            html.Iframe(
                src=f'/map/{self.area["code"]}/charities?c={self.filters}',
                style={
                    'border': 0,
                    'width': '100%',
                    'height': '100%',
                }
            ),
        ])

    @classmethod
    def import_data(cls, datadir=None):
        import pandas as pd

        results = pd.read_csv(cls.WPC_URL, index_col='ccode1')
        candidates = pd.read_csv(cls.DEMOCLUB_URL, index_col='id')

        if datadir is None:
            datadir = os.path.join(cls.datadir, cls.subpage)

        if not os.path.exists(datadir):
            os.mkdir(datadir)

        for i in results.index:
            filename = os.path.join(datadir, f'{i}.json')
            constituency = json.loads(results.loc[i, :].to_json())
            constituency['candidates'] = json.loads(
                candidates.loc[candidates["post_id"] == f'WMC:{i}', :].to_json(orient='records')
            )

            with open(filename, 'w') as a:
                json.dump(constituency, a)
