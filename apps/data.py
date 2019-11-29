import os
import json

areas_file = './data/areas.json'
if os.path.exists(areas_file):
    with open(areas_file) as areas_file_:
        AREAS = json.load(areas_file_)["areas"]

def fetch_area(area_code):
    area = [a for a in AREAS if a['code'] == area_code]
    if len(area) == 1:
        return area[0]
    return None


def fetch_areas():
    return AREAS


def get_boundary(area_code, area_type=None):
    if isinstance(area_type, str) and area_type in ['ward', 'lsoa']:
        f = f'./data/boundaries/{area_code}_{area_type}.geojson'
    else:
        f = f'./data/boundaries/{area_code}.geojson'
    if os.path.exists(f):
        with open(f) as a:
            return json.load(a)
    return None
