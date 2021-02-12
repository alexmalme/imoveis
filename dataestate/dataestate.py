# %%
# %%
import concurrent.futures
import math
import re
import sqlite3
import time
from collections.abc import Iterable

import numpy as np
import pandas as pd
from scipy import stats

# TODO - NOME DO ARQUIVO BANCO DE DADOS
dbpath = ''
# %%
time_today = time.strftime("%Y_%m_%d_%H_%M")
# %%
conn = sqlite3.connect(dbpath)
c = conn.cursor()
df = pd.read_sql('SELECT * FROM inbox', con=conn,
                 parse_dates=['AnuncioDataCaptura', 'AnuncioAtualizadoEm', 'AnuncioCriadoEm'])
conn.close()
# %%
df.loc[:, "PrecoVenda"] = df["PrecoVenda"].astype("int")
# %%
df['PrecoM2'] = df['PrecoVenda'] / df['AreaUtil']
# %%
df.loc[:, 'AnuncioEnderecoLatitude'] = df['AnuncioEnderecoLatitude'].astype(
    float)
# %%
df.loc[:, 'AnuncioEnderecoLongitude'] = df['AnuncioEnderecoLongitude'].astype(
    float)
# %%
lista_lat_lon = [*zip(df.loc[~df['AnuncioEnderecoLatitude'].isnull(), "AnuncioEnderecoLatitude"],
                      df.loc[~df['AnuncioEnderecoLongitude'].isnull(), "AnuncioEnderecoLongitude"])]
df["LatitudeLongitude"] = [
    *zip(df['AnuncioEnderecoLatitude'], df['AnuncioEnderecoLongitude'])]
# %%

# %%
df = df[df["AnuncioDescricao"].str.contains(
    "leil[aãoões]+|[extra]+judicial|retomad[ao]+|na planta|lan[cç]+amento|valor de entrada|entrada de [rR$\d.,]+",
    na=False, case=False) == False]


# %%
class GeoLocation:
    MIN_LAT = math.radians(-90)
    MAX_LAT = math.radians(90)
    MIN_LON = math.radians(-180)
    MAX_LON = math.radians(180)

    EARTH_RADIUS = 6378140  # meters equador

    @classmethod
    def from_degrees(cls, deg_lat, deg_lon):
        rad_lat = math.radians(deg_lat)
        rad_lon = math.radians(deg_lon)
        return GeoLocation(rad_lat, rad_lon, deg_lat, deg_lon)

    @classmethod
    def from_radians(cls, rad_lat, rad_lon):
        deg_lat = math.degrees(rad_lat)
        deg_lon = math.degrees(rad_lon)
        return GeoLocation(rad_lat, rad_lon, deg_lat, deg_lon)

    def __init__(
            self,
            rad_lat,
            rad_lon,
            deg_lat,
            deg_lon
    ):
        self.rad_lat = float(rad_lat)
        self.rad_lon = float(rad_lon)
        self.deg_lat = float(deg_lat)
        self.deg_lon = float(deg_lon)
        self._check_bounds()

    def __str__(self):
        degree_sign = u'\N{DEGREE SIGN}'
        return ("({0:.4f}deg, {1:.4f}deg) = ({2:.6f}rad, {3:.6f}rad)").format(
            self.deg_lat, self.deg_lon, self.rad_lat, self.rad_lon)

    def _check_bounds(self):
        if (self.rad_lat < GeoLocation.MIN_LAT
                or self.rad_lat > GeoLocation.MAX_LAT
                or self.rad_lon < GeoLocation.MIN_LON
                or self.rad_lon > GeoLocation.MAX_LON):
            raise Exception("Illegal arguments")

    def distance_to(self, other, radius=EARTH_RADIUS):
        '''
        Computes the great circle distance between this GeoLocation instance
        and the other.
        '''
        return radius * math.acos(
            math.sin(self.rad_lat) * math.sin(other.rad_lat) +
            math.cos(self.rad_lat) * math.cos(other.rad_lat) *
            math.cos(self.rad_lon - other.rad_lon)
        )

    def bounding_locations(self, distance, radius=EARTH_RADIUS):
        '''
        Computes the bounding coordinates of all points on the surface
        of a sphere that has a great circle distance to the point represented
        by this GeoLocation instance that is less or equal to the distance argument.

        Param:
            distance - the distance from the point represented by this GeoLocation
                       instance. Must be measured in the same unit as the radius
                       argument (which is kilometers by default)

            radius   - the radius of the sphere. defaults to Earth's radius.

        Returns a list of two GeoLoations - the SW corner and the NE corner - that
        represents the bounding box.
        '''

        if radius < 0 or distance < 0:
            raise Exception("Illegal arguments")

        # angular distance in radians on a great circle
        rad_dist = distance / radius

        min_lat = self.rad_lat - rad_dist
        max_lat = self.rad_lat + rad_dist

        if min_lat > GeoLocation.MIN_LAT and max_lat < GeoLocation.MAX_LAT:
            delta_lon = math.asin(math.sin(rad_dist) / math.cos(self.rad_lat))

            min_lon = self.rad_lon - delta_lon
            if min_lon < GeoLocation.MIN_LON:
                min_lon += 2 * math.pi

            max_lon = self.rad_lon + delta_lon
            if max_lon > GeoLocation.MAX_LON:
                max_lon -= 2 * math.pi
        # a pole is within the distance
        else:
            min_lat = max(min_lat, GeoLocation.MIN_LAT)
            max_lat = min(max_lat, GeoLocation.MAX_LAT)
            min_lon = GeoLocation.MIN_LON
            max_lon = GeoLocation.MAX_LON

        return [GeoLocation.from_radians(min_lat, min_lon),
                GeoLocation.from_radians(max_lat, max_lon)]


# %%
def locator(lat, lon, distances=75):
    loc = GeoLocation.from_degrees(lat, lon)
    distance = int(distances)
    SW_loc, NE_loc = loc.bounding_locations(distance)
    SW_loc = float(loc.distance_to(SW_loc)) / 100000
    NE_loc = float(loc.distance_to(NE_loc)) / 100000
    return (NE_loc, SW_loc)


# %%
def find_num(palavra):
    rex = re.compile(r'(\d+)')
    try:
        w = rex.search(str(palavra)).group(1)
    except:
        w = 0
    return float(w)


def find_num_all(num):
    rex = re.compile(r'(\d+)')
    try:
        w = "".join(rex.findall(str(num)))
    except:
        w = 0
    return int(w)


def find_words(x):
    try:
        rex = re.compile(r'(\w+)')
        word_ = ' '.join([*rex.findall(str(x))]).strip()
    except:
        word_ = x
    return word_


def find_word(x):
    try:
        word_ = re.compile(r'(\w+)').search(str(x)).group(1)
    except:
        word_ = x
    return word_


# %%
def df_builder_bairro(df, bairro):
    df_clean = df[df['AnuncioEnderecoBairro'] == bairro]
    return df_clean


# %%
def df_clusters_residential(df):
    dict_clusters = {}
    bairro_iter = set(df['AnuncioEnderecoBairro'])
    # df = df_filter_columns(df)
    list_bairro = [*bairro_iter]
    for a in list_bairro:
        dict_clusters[str(a)] = df_builder_bairro(df, a)
    return dict_clusters


# %%
def df_clusters_size(df):
    df = df.copy()
    # limpar outliers
    # df = self.drop_numerical_outliers_all(df)
    df = drop_numerical_outliers_columns(df)
    # Essa função cria colunas com as médias/medianas
    # tirar mediana bairro/metragem/com vaga
    # filtrado apenas por metragem e vaga
    df['MedianaBairroAreaTotal'] = 0
    df['MedianaBairroAreaUtil'] = 0
    df.loc[
        (df['AreaUtil'] > 0) & (df['AreaUtil'] <= 30) & (df['VagasBool'] == True), ['MedianaBairroAreaUtil']] = \
        df[(df['AreaUtil'] > 0) & (df['AreaUtil'] <= 30) & (df['VagasBool'] == True)]['PrecoVenda'].median(
            skipna=True)

    df.loc[
        (df['AreaUtil'] > 30) & (df['AreaUtil'] <= 60) & (df['VagasBool'] == True), ['MedianaBairroAreaUtil']] = \
        df[(df['AreaUtil'] > 30) & (df['AreaUtil'] <= 60) & (df['VagasBool'] == True)]['PrecoVenda'].median(
            skipna=True)

    df.loc[
        (df['AreaUtil'] > 60) & (df['AreaUtil'] <= 80) & (df['VagasBool'] == True), ['MedianaBairroAreaUtil']] = \
        df[(df['AreaUtil'] > 60) & (df['AreaUtil'] <= 80) & (df['VagasBool'] == True)]['PrecoVenda'].median(
            skipna=True)

    df.loc[
        (df['AreaUtil'] > 80) & (df['AreaUtil'] <= 120) & (df['VagasBool'] == True), ['MedianaBairroAreaUtil']] = \
        df[(df['AreaUtil'] > 80) & (df['AreaUtil'] <= 120) & (df['VagasBool'] == True)]['PrecoVenda'].median(
            skipna=True)

    df.loc[(df['AreaUtil'] > 120) & (df['VagasBool'] == True), ['MedianaBairroAreaUtil']] = \
        df[(df['AreaUtil'] > 120) & (df['VagasBool'] == True)
           ]['PrecoVenda'].median(skipna=True)

    # tirar mediana bairro/metragem/sem vaga
    # filtrado apenas por metragem e vaga
    df.loc[
        (df['AreaUtil'] > 0) & (df['AreaUtil'] <= 30) & (df['VagasBool'] == False), ['MedianaBairroAreaUtil']] = \
        df[(df['AreaUtil'] > 0) & (df['AreaUtil'] <= 30) & (df['VagasBool'] == False)]['PrecoVenda'].median(
            skipna=True)

    df.loc[
        (df['AreaUtil'] > 30) & (df['AreaUtil'] <= 60) & (df['VagasBool'] == False), ['MedianaBairroAreaUtil']] = \
        df[(df['AreaUtil'] > 30) & (df['AreaUtil'] <= 60) & (df['VagasBool'] == False)]['PrecoVenda'].median(
            skipna=True)

    df.loc[
        (df['AreaUtil'] > 60) & (df['AreaUtil'] <= 80) & (df['VagasBool'] == False), ['MedianaBairroAreaUtil']] = \
        df[(df['AreaUtil'] > 60) & (df['AreaUtil'] <= 80) & (df['VagasBool'] == False)]['PrecoVenda'].median(
            skipna=True)

    df.loc[
        (df['AreaUtil'] > 80) & (df['AreaUtil'] <= 120) & (df['VagasBool'] == False), ['MedianaBairroAreaUtil']] = \
        df[(df['AreaUtil'] > 80) & (df['AreaUtil'] <= 120) & (df['VagasBool'] == False)]['PrecoVenda'].median(
            skipna=True)

    df.loc[(df['AreaUtil'] > 120) & (df['VagasBool'] == False), ['MedianaBairroAreaUtil']] = \
        df[(df['AreaUtil'] > 120) & (df['VagasBool'] == False)
           ]['PrecoVenda'].median(skipna=True)

    # mediana PrecoVenda/m2 rua
    df = df.copy().reindex()
    df['MedianaPrecoM2Rua'] = df['AnuncioEnderecoCep'].apply(
        lambda x: stats.gmean(df.loc[df["AnuncioEnderecoCep"] == x, "PrecoM2"]))
    df["CountMedianaPrecoM2Rua"] = df.groupby('AnuncioEnderecoCep')[
        'PrecoM2'].transform('count')
    return df


# %%
def drop_numerical_outliers_all(df, zthresh=2):
    # Constrains will contain `True` or `False` depending on if it is a value below the threshold.
    constrains = df.select_dtypes(include=[np.number]).apply(lambda x: np.abs(stats.zscore(x)) < zthresh) \
        .all(axis=1)
    # Drop (inplace) values set to be rejected
    df.drop(df.index[~constrains], inplace=True)
    return df


# %%
def drop_numerical_outliers_columns(df, preco_min=100000, preco_max=10000000, quartos=6, metragem_min=15,
                                    metragem_max=300):
    df = df[(df["PrecoVenda"] >= preco_min) & (df["PrecoVenda"] <= preco_max)]
    df = df[df["AnuncioQuartos"] <= quartos]
    df = df[(df["AreaTotal"] >= metragem_min) &
            (df["AreaTotal"] <= metragem_max)]
    return df


# %%
def relacao(value_, ids, dicio, droped_lls):
    val = dicio[value_]
    lat_min = float(val[0][0])
    lon_min = float(val[0][1])
    lat_max = float(val[1][0])
    lon_max = float(val[1][1])
    lls = []
    # print(lat_min, lon_min, lat_max, lon_max)
    for m in droped_lls:
        # print(m, m[0], m[1])
        if m != None:
            if type(m) == str:
                m = m.strip().split(",")
                m[0] = "".join([i for i in m[0] if i in [
                               '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-']])
                m[0] = float(m[0])
                m[1] = "".join([i for i in m[1] if i in [
                               '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-']])
                m[1] = float(m[1])
        if m[0] != None and m[1] != None:
            if float(m[0]) >= lat_min and float(m[0]) <= lat_max and float(m[1]) >= lon_min and float(m[1]) <= lon_max:
                lls.append(m)
                yield lls, ids


# %%
def yielder(df):
    df = df.copy().reindex()
    lis_se = []
    lista_lat_lon = [*zip(df.loc[~df['AnuncioEnderecoLatitude'].isnull(), "AnuncioEnderecoLatitude"],
                          df.loc[~df['AnuncioEnderecoLongitude'].isnull(), "AnuncioEnderecoLongitude"])]
    for i in lista_lat_lon:
        if isinstance(i, Iterable) and i[0] < 0 and i[1] < 0:
            # print(i[0], i[1])
            MediaAgrupadaValidaInvestimentoPrecoVenda = (locator(i[0], i[1]))
            lis_se.append(MediaAgrupadaValidaInvestimentoPrecoVenda[0])
    df['LoccsSe'] = None
    df.loc[(df['AnuncioEnderecoLatitude'].notnull()) & (
        df['AnuncioEnderecoLongitude'].notnull()), 'LoccsSe'] = lis_se
    df['LatMinSe'] = df['AnuncioEnderecoLatitude'] - df['LoccsSe']
    df['LonMinSe'] = df['AnuncioEnderecoLongitude'] - df['LoccsSe']
    df['LatMaxSe'] = df['AnuncioEnderecoLatitude'] + df['LoccsSe']
    df['LonMaxSe'] = df['AnuncioEnderecoLongitude'] + df['LoccsSe']
    LLMin = [*zip(df['LatMinSe'], df['LonMinSe'])]
    LLMax = [*zip(df['LatMaxSe'], df['LonMaxSe'])]
    df['LLMin'] = LLMin
    df['LLMax'] = LLMax
    droped = df.drop_duplicates('LatitudeLongitude')
    idx = droped['LatitudeLongitude']
    val_min = droped['LLMin']
    val_max = droped['LLMax']
    dicio = {}
    for i, mi, ma in zip(idx, val_min, val_max):
        dicio[i] = [mi, ma]
    LatitudeLongitude = list(df['LatitudeLongitude'])
    LLMin = list(df['LLMin'])
    LLMax = list(df['LLMax'])
    idxs = list(df.index)
    droped_lls = list(droped['LatitudeLongitude'])
    dicio_relacoes_lls = {}
    dicio_relacoes_ids = {}
    for value_, ids in zip(LatitudeLongitude, idxs):
        # print(value_, ids, dicio, droped_lls)
        rela = relacao(value_, ids, dicio, droped_lls)
        for llss, i in rela:
            dicio_relacoes_lls[value_] = llss
            if llss:
                dicio_relacoes_ids.setdefault(value_, []).append(i)
    df['Relacoes'] = df['LatitudeLongitude'].map(dicio_relacoes_lls)
    df["IdsRelacoes"] = df['LatitudeLongitude'].map(dicio_relacoes_ids)
    df["CountRelacoes"] = df["IdsRelacoes"].apply(
        lambda x: len(x) if isinstance(x, Iterable) else x)
    df['MedianaPrecoRelacoes'] = df['Relacoes'].apply(
        lambda x: stats.gmean(df[df['LatitudeLongitude'].isin(x)]['PrecoVenda']).round() if isinstance(x,
                                                                                                       Iterable) else x)
    df['MedianaM2Relacoes'] = df['Relacoes'].apply(
        lambda x: stats.gmean(df[df['LatitudeLongitude'].isin(x)]['PrecoM2']).round() if isinstance(x, Iterable) else x)
    df['MediaM2'] = df.loc[:, ['MedianaPrecoM2Rua', 'MedianaM2Relacoes']].mean(
        axis=1, skipna=True).round()
    df["CountMediaM2"] = df["CountMedianaPrecoM2Rua"] + df["CountRelacoes"]
    df['MediaPreco'] = df.loc[:, ['MedianaBairroAreaTotal',
                                  'MedianaPrecoRelacoes']].mean(axis=1, skipna=True).round()
    df.loc[(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 50), 'MediaAgrupadaValidaInvestimentoPrecoVenda'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 0) & (df['AreaTotal'] <= 50), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
            lambda x: x.mean(skipna=True)).round()
    df.loc[(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 50), 'CountMediaAgrupadaValidaInvestimentoPrecoVenda'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 0) & (df['AreaTotal'] <= 50), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
            'count')
    df.loc[(df['AreaTotal'] > 50) & (df['AreaTotal'] <= 90), 'MediaAgrupadaValidaInvestimentoPrecoVenda'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 50) & (df['AreaTotal'] <= 90), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
            lambda x: x.mean(skipna=True)).round()
    df.loc[(df['AreaTotal'] > 50) & (df['AreaTotal'] <= 90), 'CountMediaAgrupadaValidaInvestimentoPrecoVenda'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 50) & (df['AreaTotal'] <= 90), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
            'count')
    df.loc[(df['AreaTotal'] > 90) & (df['AreaTotal'] <= 150), 'MediaAgrupadaValidaInvestimentoPrecoVenda'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 90) & (df['AreaTotal'] <= 150), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
            lambda x: x.mean(skipna=True)).round()
    df.loc[(df['AreaTotal'] > 90) & (df['AreaTotal'] <= 150), 'CountMediaAgrupadaValidaInvestimentoPrecoVenda'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 90) & (df['AreaTotal'] <= 150), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
            'count')
    df.loc[df['AreaTotal'] > 150, 'MediaAgrupadaValidaInvestimentoPrecoVenda'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 150), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
            lambda x: x.mean(skipna=True)).round()
    df.loc[df['AreaTotal'] > 150, 'CountMediaAgrupadaValidaInvestimentoPrecoVenda'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 150), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
            'count')
    df.loc[(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 120), 'MediaAgrupadaValidaInvestimentoM2'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 0) & (df['AreaTotal'] <= 120), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoM2'].transform(
            lambda x: x.median(skipna=True)).round()
    df.loc[(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 120), 'CountMediaAgrupadaValidaInvestimentoM2'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 0) & (df['AreaTotal'] <= 120), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoM2'].transform(
            'count')
    df.loc[df['AreaTotal'] > 120, 'MediaAgrupadaValidaInvestimentoM2'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 120), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoM2'].transform(
            lambda x: x.median(skipna=True)).round()
    df.loc[df['AreaTotal'] > 120, 'CountMediaAgrupadaValidaInvestimentoM2'] = \
        df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 120), :].groupby(
            ['AnuncioEnderecoCep', 'AnuncioEnderecoBairro', 'AnuncioQuartos', 'VagasBool'])['PrecoM2'].transform(
            'count')
    df['ValidaInvestimento'] = False
    df.loc[
        (df['PrecoM2'] / 0.64 <= df['MediaM2'])
        & (df['PrecoM2'] / 0.64 <= df['MediaAgrupadaValidaInvestimentoM2'])
        & (df['PrecoM2'] / 0.64 <= df['MedianaM2Relacoes']), 'ValidaInvestimento'
    ] = True
    df['Porcentagem'] = ((df['MediaAgrupadaValidaInvestimentoPrecoVenda'] - df['PrecoVenda']) / df['PrecoVenda']).round(
        2) * 100
    # df['PorcentagemTexto'] = df['porcentagem'].apply(lambda x: "{}%".format(re.compile(r'(\d+)').search(str(
    # x)).group(1) if x != '' else x))
    df['PorcentagemTexto'] = df['Porcentagem'].apply(
        lambda x: str(x)[:3].replace('.', '') + '%' if x != '' else x)
    yield df


# %%

# %%
dict_cluster = df_clusters_residential(df)
with concurrent.futures.ProcessPoolExecutor() as executor:
    dict_size = [executor.submit(df_clusters_size, dict_cluster[i])
                 for i in dict_cluster]
# %%
frames = []
for i in concurrent.futures.as_completed(dict_size):
    vc = yielder(i.result())
    for x in vc:
        frames.append(x)
# %%
frames = pd.concat(frames, ignore_index=True).reindex()
# frames.drop_duplicates(subset = "LinkHref", inplace = True)
# %%
frames.loc[:, 'AnuncioAtualizadoEm'] = frames['AnuncioAtualizadoEm'].apply(
    lambda x: pd.to_datetime(x).date() if x != None else x)
frames.loc[:, 'AnuncioCriadoEm'] = frames['AnuncioCriadoEm'].apply(
    lambda x: pd.to_datetime(x).date() if x != None else x)
frames.loc[:, 'AnuncioDataCaptura'] = frames['AnuncioDataCaptura'].apply(
    lambda a: pd.to_datetime(a).date() if a != None else a)
frames.loc[:, 'AnuncioAtualizadoEm'] = frames['AnuncioAtualizadoEm'].astype(
    'datetime64')
frames.loc[:, 'AnuncioCriadoEm'] = frames['AnuncioCriadoEm'].astype(
    'datetime64')
frames.loc[:, 'AnuncioDataCaptura'] = frames['AnuncioDataCaptura'].astype(
    'datetime64')
# %%
frames = frames.drop_duplicates('LinkHref', keep='first')
# %%
# frames.to_excel(f"tudo_{time_today}.xlsx")
frames.to_csv(f"tudo_{time_today}.csv", sep="|",
              encoding='utf-8', index=False, index_label=False)
conn = sqlite3.connect(dbpath)
c = conn.cursor()
c.execute('DROP TABLE tudolimpo')
c.execute("""CREATE TABLE tudolimpo(
            AuncioAndares,
            AnuncioAnuncianteContatoTelefone,
            AnuncioAtualizadoEm,
            AnuncioBanheiros,
            AnuncioCriadoEm,
            AnuncioDataCaptura,
            AnuncioDescricao,
            AnuncioEnderecoBairro,
            AnuncioEnderecoCep,
            AnuncioEnderecoCidade,
            AnuncioEnderecoComplemento,
            AnuncioEnderecoEstado,
            AnuncioEnderecoLatitude,
            AnuncioEnderecoLongitude,
            AnuncioEnderecoRua,
            AnuncioEnderecoRuaNumero,
            AnuncioEnderecoZona,
            AnuncioExternoId,
            AnuncioFacilidades,
            AnuncioInfoPrecoIptuAnual,
            AnuncioInfoPrecoNegociolabel,
            AnuncioInfoPrecoValorCondominio,
            AnuncioPortal,
            AnuncioQuartos,
            AnuncioSubTitulo,
            AnuncioSuites,
            AnuncioTitulo,
            AnuncioUnidadeTipos,
            AnuncioUnidadesporAndar,
            AnuncioVagasGaragem,
            AreaTotal,
            AreaUtil,
            ContaEmailPrincipal,
            ContaEnderecoCobrancaBairro,
            ContaEnderecoCobrancaCep,
            ContaEnderecoCobrancaCidade,
            ContaEnderecoCobrancaComplemento,
            ContaEnderecoCobrancaEstado,
            ContaEnderecoCobrancaRua,
            ContaEnderecoCobrancaRuaNumero,
            ContaEnderecoEntregaBairro,
            ContaEnderecoEntregaCep,
            ContaEnderecoEntregaCidade,
            ContaEnderecoEntregaComplemento,
            ContaEnderecoEntregaEstado,
            ContaEnderecoEntregaPais,
            ContaEnderecoEntregaRua,
            ContaEnderecoEntregaRuaNumero,
            ContaIdentidadeNumero,
            ContaNome,
            ContaSiteURL,
            ContaTelefonePrincipal,
            FinalidadeImovel,
            ImovelNovoUsado,
            LatitudeLongitude,
            LinkHref,
            Porcentagem,
            PrecoAluguel,
            PrecoAntigo,
            PrecoM2,
            PrecoReais,
            PrecoVenda,
            TipoAnunciante,
            TipoImovel,
            VagasBool,
            WhatsApp,
            MedianaBairroAreaTotal,
            MedianaBairroAreaUtil,
            MedianaPrecoM2Rua,
            CountMedianaPrecoM2Rua,
            LoccsSe,
            LatMinSe,
            LonMinSe,
            LatMaxSe,
            LonMaxSe,
            LLMin,
            LLMax,
            Relacoes,
            IdsRelacoes,
            CountRelacoes,
            MedianaPrecoRelacoes,
            MedianaM2Relacoes,
            MediaM2,
            CountMediaM2,
            MediaPreco,
            MediaAgrupadaValidaInvestimentoPrecoVenda,
            CountMediaAgrupadaValidaInvestimentoPrecoVenda,
            MediaAgrupadaValidaInvestimentoM2,
            CountMediaAgrupadaValidaInvestimentoM2,
            ValidaInvestimento,
            PorcentagemTexto)""")
conn.commit()
f = frames.copy()
f['LatitudeLongitude'] = f['LatitudeLongitude'].apply(lambda x: str(x)[1:-1])
f['LLMin'] = f['LLMin'].apply(lambda x: str(x)[1:-1])
f['LLMax'] = f['LLMax'].apply(lambda x: str(x)[1:-1])
f['Relacoes'] = f['Relacoes'].apply(
    lambda x: str(x).replace('(', '[').replace(')', ']'))
f['IdsRelacoes'] = f['IdsRelacoes'].apply(
    lambda x: str(x).replace('(', '[').replace(')', ']'))
f.to_sql('tudolimpo', conn, if_exists='replace', index=False)
conn.commit()
c.close()
conn.close()


# %%
invest_validado = frames[frames["ValidaInvestimento"] == True]
# %%
invest_validado.loc[:, 'AnuncioAtualizadoEm'] = invest_validado['AnuncioAtualizadoEm'].apply(
    lambda x: pd.to_datetime(x).date() if x != None else x)
invest_validado.loc[:, 'AnuncioCriadoEm'] = invest_validado['AnuncioCriadoEm'].apply(
    lambda x: pd.to_datetime(x).date() if x != None else x)
invest_validado.loc[:, 'AnuncioDataCaptura'] = invest_validado['AnuncioDataCaptura'].apply(
    lambda a: pd.to_datetime(a).date() if a != None else a)
# %%
invest_validado.loc[:, 'AnuncioAtualizadoEm'] = invest_validado['AnuncioAtualizadoEm'].astype(
    'datetime64')
invest_validado.loc[:, 'AnuncioCriadoEm'] = invest_validado['AnuncioCriadoEm'].astype(
    'datetime64')
invest_validado.loc[:, 'AnuncioDataCaptura'] = invest_validado['AnuncioDataCaptura'].astype(
    'datetime64')

# %%
# invest_validado.to_excel(f"investimento_validado_{time_today}.xlsx", engine='xlsxwriter', index='index')
# %%
