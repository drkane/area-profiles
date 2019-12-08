from flask import Blueprint, render_template, request, current_app

from sources import get_source_cls
from .data import fetch_area, get_boundary

maps = Blueprint('maps', __name__,
                 template_folder='templates')


@maps.route('/<area_code>/<subpage>')
@maps.route('/<area_code>')
def show(area_code, subpage=None):

    area = fetch_area(area_code)
    data = get_source_cls(subpage, area['type'])(
        area, datadir=current_app.config['DATA_DIR'])

    params = dict(
        access_token='pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw',
        boundary=get_boundary(area['code']),
        lsoa_boundary=get_boundary(area['code'], 'lsoa'),
        ward_boundary=get_boundary(area['code'], 'ward'),
        area=area,
        lsoa_fill={},
        markers={},
    )
    params.update(**data.map_params(request))

    return render_template(
        'map.html',
        **params
    )


@maps.route('/locator/<area_code>')
def locator_map(area_code):
    boundary = get_boundary(area_code)
    return render_template(
        'map_locator.html',
        area_code=area_code,
        boundary=boundary,
    )
