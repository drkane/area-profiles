import os
import json

from flask import current_app

AREA_TYPES = {
    'pcon': 'Parliamentary Constituency',
    'la': 'Local Authority',
    'la_upper': 'Local Authority',
    'la_lower': 'Local Authority',
}

def fetch_area(area_code):
    areas = fetch_areas()
    area = [a for a in areas if a['code'] == area_code]
    if len(area) == 1:
        return area[0]
    return None


def fetch_areas(datadir=None):
    if datadir is None:
        datadir = current_app.config.get('DATA_DIR', './data')
    areas_file = os.path.join(datadir, 'areas.json')
    if os.path.exists(areas_file):
        with open(areas_file) as areas_file_:
            return json.load(areas_file_)["areas"]


def get_boundary(area_code, area_type=None):
    datadir = os.path.join(current_app.config['DATA_DIR'], 'boundaries')
    if isinstance(area_type, str) and area_type in ['ward', 'lsoa']:
        f = os.path.join(datadir, f'{area_code}_{area_type}.geojson')
    else:
        f = os.path.join(datadir, f'{area_code}.geojson')
    if os.path.exists(f):
        with open(f) as a:
            return json.load(a)
    return None
