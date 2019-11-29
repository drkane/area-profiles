import flask
import dash

from apps.maps import maps
from sources import import_data

external_stylesheets = [
    "https://unpkg.com/tachyons@4.10.0/css/tachyons.min.css",
    "https://fonts.googleapis.com/css?family=Archivo|Raleway",
]

server = flask.Flask(__name__, static_url_path='/static')
server.register_blueprint(maps, url_prefix='/map')
server.cli.add_command(import_data)

app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=external_stylesheets,
)
app.title = 'Area Profiles'
app.config.suppress_callback_exceptions = True
