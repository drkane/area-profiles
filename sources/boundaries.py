import os
import geopandas
from tqdm import tqdm

# Location of the latest geometries to use
GEO_URLS = dict(
    pcon=('https://opendata.arcgis.com/datasets/094f326b0b1247e3bcf1eb7236c24679_0.geojson', 'pcon18'),
    la_lower=(
        'https://opendata.arcgis.com/datasets/2c5b8eb836c7475ba3b305106ac9dfc3_0.geojson', 'lad18'),
    la_upper=(
        'https://opendata.arcgis.com/datasets/0de4288db3774cb78e45b8b74e9eab31_0.geojson', 'ctyua19'),
    ward=('https://opendata.arcgis.com/datasets/496e0b4fb23e413aa4feb6bd193bc3d1_0.geojson', 'wd19'),
    lsoa=('https://opendata.arcgis.com/datasets/da831f80764346889837c72508f046fa_2.geojson', 'lsoa11'),
)

def fetch_boundaries(datadir='./data'):

    datadir = os.path.join(datadir, 'boundaries')

    # fetch the boundary data
    print("fetching boundaries")
    boundaries = {
        g: geopandas.read_file(u[0]).rename(columns={
            f'{u[1]}cd': 'code',
            f'{u[1]}nm': 'name_en',
            f'{u[1]}nmw': 'name_cy'
        }).set_index('code')
        for g, u in tqdm(GEO_URLS.items())
    }

    # turn into area geojson files
    for area_type in ['pcon', 'la_upper', 'la_lower']:
        print(f"saving boundaries for {area_type}")
        for i in tqdm(boundaries[area_type].head().index):

            # skip areas that are in both la_upper and la_lower
            if area_type == 'la_upper' and i in boundaries['la_lower'].index:
                continue

            # save the main boundary
            boundaries[area_type].loc[[i]].reset_index().to_file(
                os.path.join(datadir, f"{i}.geojson"), driver="GeoJSON")

            # save the intersecting lsoa boundaries
            lsoa = boundaries['lsoa'][
                boundaries['lsoa'].geometry.intersects(
                    boundaries[area_type].loc[i].geometry
                )
            ]
            if lsoa.empty:
                lsoa.reset_index().to_file(
                    os.path.join(datadir, f"{i}_lsoa.geojson"),
                    driver="GeoJSON"
                )

            # save the intersecting ward boundaries
            ward = boundaries['ward'][
                boundaries['ward'].geometry.intersects(
                    boundaries[area_type].loc[i].geometry
                )
            ]
            if ward.empty:
                ward.reset_index().to_file(
                    os.path.join(datadir, f"{i}_ward.geojson"),
                    driver="GeoJSON"
                )
