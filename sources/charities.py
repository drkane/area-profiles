import json
import os

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
# from dash.dependencies import Input, Output, State

from apps.utils import scale_value, correct_titlecase
from .datapage import DataPage


class CharityData(DataPage):

    subpage = 'charities'

    def __init__(self, area, filters=None):
        self.area = area
        self.filters = self._set_filters(filters)
        self.data = self._fetch_data()


    def _fetch_data(self):
        f = f"./data/charities/{self.area['code']}.json"
        if os.path.exists(f):
            with open(f) as a:
                return json.load(a)
        return None


    def _set_filters(self, filters):
        if filters is None or filters.get('exclusions') is None or 'exclude' in filters.get('exclusions_link', '').lower():
            data_filter = 'exclude_sch_uni_and_national'
        else:
            data_filter = 'exclude_sch_uni'
        return data_filter


    def _fig_topstats(self):
        data = self.data[self.filters]
        return self.show_figure(
            html.Ul(className='list pl0', children=[
                html.Li(className='f6 mv1 lh-copy', children=[
                    html.A(
                        className='link underline-hover near-black',
                        children=correct_titlecase(char[1]["name"]),
                        href=f'https://beta.charitycommission.gov.uk/charity-details/?regId={char[0]}&subId=0',
                        target="_blank"
                    ),
                    " ",
                    # html.Small(f"({char[0]})"),
                    "(£{})".format(scale_value(char[1].get(
                        "spending"), True)),
                    # html.Small("({:.0%})".format(char[1]["spending"] / data["spending"])),
                ])
                for k, char in enumerate(data["top"].items())
            ]),
            'Largest charities'
        )

    def _fig_spendingchart(self):
        data = self.data[self.filters]
        return self.show_figure(
            dcc.Graph(
                figure=go.Figure(
                    data=[
                        go.Scatter(
                            x=list(data["financial"].keys()),
                            y=[i["spending"]
                               for i in data["financial"].values()],
                            name='Spending',
                            mode='lines',
                        )
                    ],
                    layout=go.Layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        margin=go.layout.Margin(l=40, r=0, t=40, b=30),
                        xaxis=dict(
                            type='category',
                            showgrid=False,
                        ),
                        yaxis=dict(
                            rangemode='tozero',
                            showgrid=False,
                            tickprefix='£',
                            showtickprefix='last',
                            showexponent='last',
                            separatethousands=True,
                        ),
                    )
                ),
                config=dict(
                    displayModeBar=False,
                ),
                style={'height': 150, 'width': '100%'},
                id='financial-history'
            ),
            'Charity spending'
        )

    def sidebar(self):
        data = self.data[self.filters]
        return [
            html.Div([
                html.Strong(className='f3 lh-copy pa0 ma0 header-font',
                            children="{:,.0f}".format(data["charities"])),
                html.Span(className='f5 lh-copy pa0 ma0',
                          children=' charities')
            ]),
            html.Div([
                html.Strong(className='f3 lh-copy pa0 ma0 header-font', children='£{}'.format(
                    scale_value(list(
                        data["financial"].items())[-1][1]["spending"])
                )),
                html.Br(),
                html.Span(className='f5 lh-copy pa0 ma0', children=' total spending by charities in {}'.format(
                    list(data["financial"].items())[-1][0]
                ))
            ]),
            # html.Div([
            #     html.Strong(className='f4 lh-copy pa0 ma0 header-font',
            #                 children='£{:,.0f}'.format(data["income"])),
            #     html.Span(className='f5 lh-copy pa0 ma0',
            #               children=' total latest spending')
            # ]),
            self._fig_topstats(),
            self._fig_spendingchart(),
        ]

    def attribution(self):
        return dcc.Markdown('''
- from the [Charity Commission](https://beta.charitycommission.gov.uk/), [OSCR](https://www.oscr.org.uk/) 
  and [CCNI](https://www.charitycommissionni.org.uk/). 
- Also includes [some of my own data](https://github.com/drkane/charity-lookups) on charities.
            ''')


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

    def map_params(self, request):
        topchar = list(self.data[self.filters]["top"].keys())
        return dict(
            config_type=self.filters,
            markers={
                "Charities": self.data['map'],
                "Largest charities": {
                    k: v
                    for k, v in self.data['map'].items()
                    if v["reg_number"] in topchar
                }
            }
        )

    @classmethod
    def import_data(cls, datadir=None):
        pass
