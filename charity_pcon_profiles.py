import datetime
import json

import pandas as pd
import requests
from tqdm import tqdm

# connection to DB
sql_con = 'postgres://postgres:postgres@localhost/charity'

# fetch charity numbers of independent schools
independent_schools = pd.read_csv(
    'https://raw.githubusercontent.com/drkane/charity-lookups/master/independent-schools-ew.csv',
    dtype='str'
)
independent_schools = independent_schools.charity_number.dropna().unique().tolist()

# fetch charity numbers of universities
universities = pd.read_csv(
    'https://raw.githubusercontent.com/drkane/charity-lookups/master/university-charity-number.csv'
)
universities = universities.OrgID.apply(lambda x: x.replace("GB-CHC-", "").replace("GB-SC-", "").replace("GB-NIC-", "NI")).dropna().unique().tolist()
oxbridge = pd.read_csv('https://github.com/drkane/charity-lookups/raw/master/oxbridge-charity-numbers.csv', dtype=str)
universities += oxbridge["Charity Number"].dropna().unique().tolist()

def financial_year_from_date(d, cutoff=3):
    if d.month <= cutoff:
        years = [str(d.year-1), str(d.year)]
    else:
        years = [str(d.year), str(d.year+1)]
    if years[0][0:2] != years[1][0:2]:
        return "-".join(years)
    return f"{years[0]}-{years[1][2:]}"

def fetch_area_data(area):
    df = pd.read_sql('''
        select cm.*, e.aims, s.scale, p.lat, p.long, p.pcon, p.oslaua
        from charity_main cm
            inner join geo_postcodes p
                on CONCAT(TRIM(LEFT(postcode, LENGTH(postcode)-3)), ' ',RIGHT(postcode, 3)) = p.pcds
            left outer join ccew_extra e
                on cm.reg_number = e.regno
            left outer join charity_scale s
                on cm.reg_number = s.reg_number
        where (p.pcon = %(pcon)s
            or p.oslaua = %(oslaua)s)
            and COALESCE(dual_registered, false) = false
    ''', sql_con, params=area, index_col='reg_number')
    df.loc[:, "independent_school"] = df.index.isin(independent_schools)
    df.loc[:, "universities"] = df.index.isin(universities)
    df.loc[:, "independent_school_or_uni"] = df.index.isin(independent_schools) | df.index.isin(universities)
    df.loc[:, "local"] = df.scale.isin(["Regional", "Local"])
    return df

def fetch_area_financials(df):
    fin = pd.read_sql('''
        select * from charity_financial
        where reg_number in ('{}')
    '''.format("', '".join(df.index.to_list())), sql_con)
    fin.loc[:, "financial_year"] = fin.fye.apply(financial_year_from_date)
    return fin

def get_financial_breakdown(fin, df):
    fyear = fin.groupby("financial_year").agg({
        "income": "sum",
        "spending": "sum",
        "reg_number": "nunique",
    })
    in_years = {}
    for i in fyear.index:
        years = i.split("-")
        if len(years[1]) == 2:
            years[1] = years[0][0:2] + years[1]
        dates = [
            datetime.date(int(years[0]), 4, 1),
            datetime.date(int(years[1]), 3, 31),
        ]
        in_year = df[(df.date_registered <= dates[1]) & ((df.date_removed > dates[1]) | df.date_removed.isnull())]
        in_years[i] = len(in_year)
    fyear.loc[:, "registered"] = pd.Series(in_years)
    fyear.loc[:, "pc_of_registered"] = (fyear.reg_number / fyear.registered)
    fyear.loc[:, "to_use"] = fyear.pc_of_registered.gt(0.8)
    return fyear[fyear.to_use][["income", "spending", "registered"]]

def get_area_data(area):

    df = fetch_area_data(area)
    fin = fetch_area_financials(df)

    configs = {
        "all": df.name.apply(lambda c: True),
        "exclude_sch_uni": df.independent_school_or_uni.ne(True),
        "exclude_national": df.local.eq(True),
        "exclude_sch_uni_and_national": df.independent_school_or_uni.ne(True) & df.local.eq(True),
    }

    data = {}

    for c, criteria in configs.items():
        df_ = df[criteria]
        data[c] = dict(
            areacode=area['pcon'],
            config=c,
            charities=len(df_[df_["active"]]),
            income=df_[df_["active"]]["income"].sum(),
            top=df_[df_["active"]].sort_values("spending", ascending=False).head(5)[
                ["name", "spending", "aims", "scale"]
            ].to_dict('index'),
        )

        fyear = get_financial_breakdown(fin[fin.reg_number.isin(df_.index)], df_)
        data[c]["financial"] = fyear.to_dict('index')

    data["map"] = df.join(pd.DataFrame(configs)).loc[df["active"], ["name", "lat", "long"] + list(configs.keys())].reset_index().to_dict('index')

    return data


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.np.integer):
            return int(obj)
        if isinstance(obj, pd.np.floating):
            return float(obj)
        if isinstance(obj, pd.np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def main():

    # fetch list of parliamentary constituencies
    r = requests.get('https://opendata.arcgis.com/datasets/1957697792a24de8a561215c26b57d12_0.geojson')
    pcon = [(f['properties']['PCON18CD'], f['properties']['PCON18NM']) for f in r.json()['features']]

    with open(f'data/areas.json', 'w') as a:
        json.dump({
            "areas": [{"code": code, "name": name, "type": "pcon"} for code, name in pcon]
        }, a, cls=NpEncoder)

    for p in tqdm(pcon):
        data = get_area_data({'pcon': p[0], 'oslaua': None})
        data["area"] = {
            "code": p[0],
            "name": p[1],
            "type": "Parliamentary Consituency",
        }
        with open(f'data/areas/{p[0]}.json', 'w') as a:
            json.dump(data, a, cls=NpEncoder)

if __name__ == '__main__':
    main()
