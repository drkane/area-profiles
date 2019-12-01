import dash_core_components as dcc
import dash_html_components as html
# import plotly.graph_objs as go


class DataPage:

    subpage = ''
    areatype_names = {
        'pcon': 'Parliamentary Constituency',
        'la': 'Local Authority',
        'la_upper': 'Local Authority',
        'la_lower': 'Local Authority',
    }
    datadir = 'data'


    def _fetch_data(self):
        pass


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

    def sidebar(self):
        return []

    def map(self):
        return []

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
