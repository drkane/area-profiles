from flask.cli import AppGroup, with_appcontext
from flask import current_app
import click

from .datapage import DataPage
from .charities import CharityData
from .election import ElectionData
from .companies import CompanyData
from .deprivation import DeprivationData
from .housing import HousingData
from .boundaries import fetch_boundaries

classes = [CharityData, CompanyData, DeprivationData, ElectionData, HousingData]
classes = {c.subpage: c for c in classes}

def get_source_cls(subpage, areatype):

    return classes.get(subpage, DataPage)

import_cli = AppGroup('import')

@click.command('import')
@click.argument('subpage')
@with_appcontext
def import_data(subpage):
    datadir = current_app.config.get('DATA_DIR', './data')
    if subpage == 'boundaries':
        fetch_boundaries(datadir=datadir)
    else:
        c = classes.get(subpage, DataPage).import_data(datadir=datadir)
