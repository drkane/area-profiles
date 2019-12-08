from flask.cli import AppGroup, with_appcontext
from flask import current_app
import click

from .datapage import DataPage
from .charities import CharityData
from .election import ElectionData
from .companies import CompanyData
from .deprivation import DeprivationData
from .boundaries import fetch_boundaries

def get_source_cls(subpage, areatype):

    if subpage == "charities":
        return CharityData
    elif subpage == "companies":
        return CompanyData
    elif subpage == "deprivation":
        return DeprivationData
    elif subpage == "elections":
        return ElectionData
    else:
        return DataPage

import_cli = AppGroup('import')

@click.command('import')
@click.argument('subpage')
@with_appcontext
def import_data(subpage):
    datadir = current_app.config.DATA_DIR
    if subpage == 'charities':
        CharityData.import_data(datadir=datadir)
    elif subpage == 'election':
        ElectionData.import_data(datadir=datadir)
    elif subpage == 'companies':
        CompanyData.import_data(datadir=datadir)
    elif subpage == 'deprivation':
        DeprivationData.import_data(datadir=datadir)
    elif subpage == 'boundaries':
        fetch_boundaries(datadir=datadir)
