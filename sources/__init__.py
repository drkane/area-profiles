from flask.cli import AppGroup
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
def import_data(subpage):
    if subpage == 'charities':
        CharityData.import_data()
    elif subpage == 'election':
        ElectionData.import_data()
    elif subpage == 'companies':
        CompanyData.import_data()
    elif subpage == 'deprivation':
        DeprivationData.import_data()
    elif subpage == 'boundaries':
        fetch_boundaries('./data/boundaries')
