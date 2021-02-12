# -*- coding: utf-8 -*-
import pandas as pd
import sqlite3
import concurrent.futures
import pycep_correios
import geopy
from geopy.geocoders import Nominatim
import re
import math
from scipy import stats
import numpy as np
import time

time_today = time.strftime("%Y_%m_%d_%H_%M")
timestamp = time.strftime("%Y%m%d%H%M")
zone = "zona_sul"

"""Como pegar os dados do sql
1 - VocÃª conecta:
conn = sqlite3.connect('/home/alx/imoveis/db/banco2')

2 - VocÃª cria o cursor
cur = conn.cursor()

3 - Executa a QUERY ou o INSERT
c = cur.execute("SELECT * FROM imoveis limit 20;")

4 - Mostrar os dados
c.fetchall()

5 - Fechar o cursor
cur.close()

6 - Fechar a conexÃ£o
conn.close()
"""

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



def find_num_all(num):
	rex = re.compile(r'(\d+)')
	try:
	    w = "".join(rex.findall(str(num)))
	except:
	    w = 0
	return int(w)

def find_num(palavra):
	rex = re.compile(r'(\d+)')
	try:
		w = rex.search(str(palavra)).group(1)
	except:
		w = 0
	return float(w)

def df_clusters_size1(df):
	df = df.copy()

	# limpar outliers
	# df = self.drop_numerical_outliers_all(df)
	# Essa função cria colunas com as médias/medianas

	# tirar mediana bairro/metragem/com vaga
	# filtrado apenas por metragem e vaga
	df['MedianaBairroAreaTotal'] = 0


	df.loc[
		(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 30) & (df['VagasBool'] == True), ['MedianaBairroAreaTotal']] = \
		df[(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 30) & (df['VagasBool'] == True)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 30) & (df['AreaTotal'] <= 60) & (df['VagasBool'] == True), ['MedianaBairroAreaTotal']] = \
		df[(df['AreaTotal'] > 30) & (df['AreaTotal'] <= 60) & (df['VagasBool'] == True)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 60) & (df['AreaTotal'] <= 80) & (df['VagasBool'] == True), ['MedianaBairroAreaTotal']] = \
		df[(df['AreaTotal'] > 60) & (df['AreaTotal'] <= 80) & (df['VagasBool'] == True)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 80) & (df['AreaTotal'] <= 120) & (df['VagasBool'] == True), ['MedianaBairroAreaTotal']] = \
		df[(df['AreaTotal'] > 80) & (df['AreaTotal'] <= 120) & (df['VagasBool'] == True)]['PrecoVenda'].median(
			skipna=True)

	df.loc[(df['AreaTotal'] > 120) & (df['VagasBool'] == True), ['MedianaBairroAreaTotal']] = \
		df[(df['AreaTotal'] > 120) & (df['VagasBool'] == True)]['PrecoVenda'].median(skipna=True)

	# tirar mediana bairro/metragem/sem vaga
	# filtrado apenas por metragem e vaga
	df.loc[
		(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 30) & (df['VagasBool'] == False), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 30) & (df['VagasBool'] == False)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 30) & (df['AreaTotal'] <= 60) & (df['VagasBool'] == False), ['MedianaBairroAreaTotal']] = \
		df[(df['AreaTotal'] > 30) & (df['AreaTotal'] <= 60) & (df['VagasBool'] == False)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 60) & (df['AreaTotal'] <= 80) & (df['VagasBool'] == False), ['MedianaBairroAreaTotal']] = \
		df[(df['AreaTotal'] > 60) & (df['AreaTotal'] <= 80) & (df['VagasBool'] == False)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 80) & (df['AreaTotal'] <= 120) & (df['VagasBool'] == False), ['MedianaBairroAreaTotal']] = \
		df[(df['AreaTotal'] > 80) & (df['AreaTotal'] <= 120) & (df['VagasBool'] == False)]['PrecoVenda'].median(
			skipna=True)

	df.loc[(df['AreaTotal'] > 120) & (df['VagasBool'] == False), ['MedianaBairroAreaTotal']] = \
		df[(df['AreaTotal'] > 120) & (df['VagasBool'] == False)]['PrecoVenda'].median(skipna=True)

	# mediana PrecoVenda/m2 rua
	df = df.copy().reindex()
	df['MedianaPrecoM2Rua'] = df.groupby('AnuncioEnderecoCep')['PrecoM2'].transform(lambda x: x.mean())
	return df

def df_clusters_size(df):
	df = df.copy()

	# limpar outliers
	# df = self.drop_numerical_outliers_all(df)
	# Essa função cria colunas com as médias/medianas

	# tirar mediana bairro/metragem/com vaga
	# filtrado apenas por metragem e vaga
	df['MedianaBairroAreaTotal'] = 0


	df.loc[
		(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 30) & (df['VagasBool'] == True), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 30) & (df['VagasBool'] == True)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 30) & (df['AreaTotal'] <= 60) & (df['VagasBool'] == True), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 30) & (df['AreaTotal'] <= 60) & (df['VagasBool'] == True)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 60) & (df['AreaTotal'] <= 80) & (df['VagasBool'] == True), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 60) & (df['AreaTotal'] <= 80) & (df['VagasBool'] == True)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 80) & (df['AreaTotal'] <= 120) & (df['VagasBool'] == True), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 80) & (df['AreaTotal'] <= 120) & (df['VagasBool'] == True)]['PrecoVenda'].median(
			skipna=True)

	df.loc[(df['AreaTotal'] > 120) & (df['VagasBool'] == True), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 120) & (df['VagasBool'] == True)]['PrecoVenda'].median(skipna=True)

	# tirar mediana bairro/metragem/sem vaga
	# filtrado apenas por metragem e vaga
	df.loc[
		(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 30) & (df['VagasBool'] == False), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 30) & (df['VagasBool'] == False)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 30) & (df['AreaTotal'] <= 60) & (df['VagasBool'] == False), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 30) & (df['AreaTotal'] <= 60) & (df['VagasBool'] == False)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 60) & (df['AreaTotal'] <= 80) & (df['VagasBool'] == False), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 60) & (df['AreaTotal'] <= 80) & (df['VagasBool'] == False)]['PrecoVenda'].median(
			skipna=True)

	df.loc[
		(df['AreaTotal'] > 80) & (df['AreaTotal'] <= 120) & (df['VagasBool'] == False), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 80) & (df['AreaTotal'] <= 120) & (df['VagasBool'] == False)]['PrecoVenda'].median(
			skipna=True)

	df.loc[(df['AreaTotal'] > 120) & (df['VagasBool'] == False), ['MedianaBairroAreaTotal']] = df[(df['AreaTotal'] > 120) & (df['VagasBool'] == False)]['PrecoVenda'].median(skipna=True)

	# mediana PrecoVenda/m2 rua
	df = df.copy().reindex()
	df['MedianaPrecoM2Rua'] = df.groupby('AnuncioEnderecoCep')['PrecoM2'].transform(lambda x: x.mean())

	return df



def df_builder_bairro(df, bairro):
	df_clean = df[df['Bairro'] == bairro]
	return df_clean



def df_clusters_residential(df):
        dict_clusters = {}
        #df = df[df['FinalidadeImovel'] == 'residencial'].reindex()
        bairro_iter = set(df['Bairro'])
        # df = df_filter_columns(df)
        list_bairro = [*bairro_iter]
        for a in list_bairro:
                dict_clusters[str(a)] = df_builder_bairro(df, a)
        return dict_clusters



def relacao(value_, ids, dicio, droped_lls):
	val = dicio[value_]
	lat_min = val[0][0]
	lon_min = val[0][1]
	lat_max = val[1][0]
	lon_max = val[1][1]
	lls = []
	for m in droped_lls:
		if m[0] >= lat_min and m[0] <= lat_max and m[1] >= lon_min and m[1] <= lon_max:
			lls.append(m)
			yield lls


def yielder(df):
	df = df.copy().reindex()
	lista_lat_lon = [*zip(df['AnuncioEnderecoLatitude'], df['AnuncioEnderecoLongitude'])]
	df['LatitudeLongitude'] = lista_lat_lon
	lis_se = []
	for i in lista_lat_lon:
		MediaAgrupadaValidaInvestimentoPrecoVenda = (locator(float(i[0]), float(i[1])))
		lis_se.append(MediaAgrupadaValidaInvestimentoPrecoVenda[0])
	df['LoccsSe'] = lis_se
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
	for value_, ids in zip(LatitudeLongitude, idxs):
		rela = relacao(value_, ids, dicio, droped_lls)
		for llss in rela:
			dicio_relacoes_lls[value_] = llss

	df['Relacoes'] = df['LatitudeLongitude'].map(dicio_relacoes_lls)

	df['MedianaPrecoRelacoes'] = df['Relacoes'].apply(
		lambda x: stats.gmean(df[df['LatitudeLongitude'].isin(x)]['PrecoVenda']).round() if x != '' else x)

	df['MedianaM2Relacoes'] = df['Relacoes'].apply(
		lambda x: stats.gmean(df[df['LatitudeLongitude'].isin(x)]['PrecoM2']).round() if x != '' else x)

	df['MediaM2'] = df.loc[:, ['MedianaPrecoM2Rua', 'MedianaM2Relacoes']].mean(axis=1, skipna=True).round()

	df['MediaPreco'] = df.loc[:, ['MedianaBairroAreaTotal', 'MedianaPrecoRelacoes']].mean(axis=1,
	                                                                                      skipna=True).round()

	df.loc[(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 50), 'MediaAgrupadaValidaInvestimentoPrecoVenda'] = df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 0) & (df['AreaTotal'] <= 50), :].groupby(
			['AnuncioEnderecoCep', 'Bairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
			lambda x: x.mean(skipna=True)).round()

	df.loc[(df['AreaTotal'] > 50) & (df['AreaTotal'] <= 90), 'MediaAgrupadaValidaInvestimentoPrecoVenda'] = df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 50) & (df['AreaTotal'] <= 90), :].groupby(
			['AnuncioEnderecoCep', 'Bairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
			lambda x: x.mean(skipna=True)).round()

	df.loc[(df['AreaTotal'] > 90) & (df['AreaTotal'] <= 150), 'MediaAgrupadaValidaInvestimentoPrecoVenda'] = df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 90) & (df['AreaTotal'] <= 150), :].groupby(
			['AnuncioEnderecoCep', 'Bairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
			lambda x: x.mean(skipna=True)).round()

	df.loc[df['AreaTotal'] > 150, 'MediaAgrupadaValidaInvestimentoPrecoVenda'] = df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 150), :].groupby(
			['AnuncioEnderecoCep', 'Bairro', 'AnuncioQuartos', 'VagasBool'])['PrecoVenda'].transform(
			lambda x: x.mean(skipna=True)).round()

	df.loc[(df['AreaTotal'] > 0) & (df['AreaTotal'] <= 120), 'MediaAgrupadaValidaInvestimentoM2'] = df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 0) & (df['AreaTotal'] <= 120), :].groupby(
			['AnuncioEnderecoCep', 'Bairro', 'AnuncioQuartos', 'VagasBool'])['PrecoM2'].transform(
			lambda x: x.median(skipna=True)).round()

	df.loc[df['AreaTotal'] > 120, 'MediaAgrupadaValidaInvestimentoM2'] = df.loc[(df['AnuncioEnderecoCep'].notna()) & (df['AreaTotal'] > 120), :].groupby(
			['AnuncioEnderecoCep', 'Bairro', 'AnuncioQuartos', 'VagasBool'])['PrecoM2'].transform(
			lambda x: x.median(skipna=True)).round()

	df['ValidaInvestimento'] = False

	df.loc[(df['PrecoVenda'] / 0.64 <= df['MediaAgrupadaValidaInvestimentoPrecoVenda']) & (
			df['PrecoVenda'] / 0.64 <= df['MediaPreco']) & (
			       df['PrecoVenda'] / 0.64 <= df['MedianaPrecoRelacoes']) & (
			       df['PrecoM2'] / 0.64 <= df['MediaM2']) & (
			       df['PrecoM2'] / 0.64 <= df['MediaAgrupadaValidaInvestimentoM2']) & (
			       df['PrecoM2'] / 0.64 <= df['MedianaM2Relacoes']), 'ValidaInvestimento'] = True

	df['Porcentagem'] = ((df['MediaAgrupadaValidaInvestimentoPrecoVenda'] - df['PrecoVenda'])  / df['PrecoVenda']).round(2) * 100
	# df['PorcentagemTexto'] = df['porcentagem'].apply(lambda x: "{}%".format(re.compile(r'(\d+)').search(str(
	# x)).group(1) if x != '' else x))

	df['PorcentagemTexto'] = df['Porcentagem'].apply(lambda x: str(x)[:3].replace('.', '') + '%' if x != '' else x)

	yield df



def lat_lon_creator(cep):
	if cep.isalnum():
		cep = str(find_num_all(cep))
		geolocator = Nominatim(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")
		location = None
		try:
			endereco = pycep_correios.get_address_from_cep(cep)
			end = " ".join([endereco['logradouro'], endereco['bairro'], endereco['cidade'], endereco['uf'], "Brazil"]).strip()
			location = geolocator.geocode(end)
			if location:
					return (location.latitude, location.longitude)
		except:
			return location

def locator(lat, lon, distances=100):
	loc = GeoLocation.from_degrees(lat, lon)
	distance = int(distances)
	SW_loc, NE_loc = loc.bounding_locations(distance)
	SW_loc = float(loc.distance_to(SW_loc)) / 100000
	NE_loc = float(loc.distance_to(NE_loc)) / 100000
	return (NE_loc, SW_loc)

conn = sqlite3.connect('/home/alx/imoveis/db/banco2')
s_one = 'SELECT * FROM imoveis WHERE AnuncioEnderecoZona = "Zona Sul";'
s_two = 'SELECT * FROM olx WHERE AnuncioEnderecoZona = "Zona Sul";'
teste = pd.read_sql(s_one, conn)
teste_olx = pd.read_sql(s_two, conn)
conn.close()
dfs = pd.concat([teste, teste_olx])
dfs.drop_duplicates(subset="LinkHref", keep="last", inplace=True)
dfs.info
dfs.drop(columns=['MedianaPrecoRelacoes',
        'MedianaM2Relacoes',
        'MediaM2',
        'MediaPreco',
        'MediaAgrupadaValidaInvestimentoPrecoVenda',
        'MediaAgrupadaValidaInvestimentoM2',
        'MedianaBairroAreaTotal',
        'MedianaPrecoM2Rua',
        'ValidaInvestimento',
        'Porcentagem',
        'PorcentagemTexto'], inplace=True)


def call_invest(df, price = 10000):
    df = df.copy()
    df = df[df['PrecoVenda'] > price]
    df[ 'ZScoreP'] = (df['PrecoVenda'] - df['PrecoVenda'].mean(skipna=True)) / df['PrecoVenda'].std(ddof=0)
    df[ 'ZScoreP'] = df['ZScoreP'].apply(lambda x: np.abs(x))
    df = df[df['ZScoreP'] < 2]
    df = df.drop(columns=['ZScoreP']).reindex()
    invs = df[df['ValidaInvestimento'] == True].drop_duplicates('LinkHref')
    # csv limpo, para visualização de quem não quer muita informação
    # agregar os textos em uma única coluna
    columns_invs = {'Bairro',
	'LinkHref',
	'ContaNome',
	'ContaEmailPrincipal',
	'ContaTelefonePrincipal',
	'ContaTelefoneCelular',
	'ContaEnderecoEntregaCep',
	'ContaEnderecoEntregaCidade',
	'ContaEnderecoEntregaRuaNumero',
	'ContaEnderecoEntregaZona',
	'ContaEnderecoEntregaRua',
	'ContaEnderecoEntregaEstado',
	'ContaEnderecoEntregaBairro',
	'ContaEnderecoEntregaComplemento',
	'ContaEnderecoCobrancaCep',
	'ContaEnderecoCobrancaCidade',
	'ContaEnderecoCobrancaRuaNumero',
	'ContaEnderecoCobrancaZona',
	'ContaEnderecoCobrancaRua',
	'ContaEnderecoCobrancaEstado',
	'ContaEnderecoCobrancaBairro',
	'ContaEnderecoCobrancaComplemento',
	'ContaIdentidadeNumero',
	'ContaSiteURL',
	'PrecoVenda',
	'TipoAnunciante',
	'AreaUtil',
	'ImovelNovoUsado',
	'AnuncioCriadoEm',
	'AnuncioExternoId',
	'AnuncioUnidadeTipos',
	'AnuncioUnidadesporAndar',
	'AnuncioAndarUnidade',
	'AnuncioVagasGaragem',
	'AnuncioAtualizadoEm',
	'AnuncioSuites',
	'AnuncioBanheiros',
	'FinalidadeImovel',
	'AnuncioQuartos',
	'AnuncioBlocos',
	'AnuncioFacilidades',
	'AnuncioDescricao',
	'AnuncioTitulo',
	'AnuncioAndares',
	'TipoImovel',
	'PrecoAluguel',
	'AnuncioEnderecoCep',
	'AnuncioEnderecoCidade',
	'AnuncioEnderecoZona',
	'AnuncioEnderecoRua',
	'AnuncioEnderecoNome',
	'AnuncioEnderecoEstado',
	'AnuncioEnderecoBairro',
	'AnuncioEnderecoComplemento',
	'AreaTotal',
	'AnuncioDiasDesdeCriacaoCod',
	'AnuncioAnuncianteContatoTelefone',
	'AnuncioInfoPrecoValorCondominio',
	'AnuncioInfoPrecoPrecodeAluguel',
	'AnuncioInfoPrecoPrecoDeVenda',
	'AnuncioInfoPrecoIptuAnual',
	'AnuncioEnderecoRuaNumero',
	'VagasBool',
	'PrecoM2',
	'MedianaBairroAreaTotal',
	'MedianaPrecoM2Rua',
	'MedianaPrecoRelacoes',
	'MedianaM2Relacoes',
	'MediaM2',
	'MediaPreco',
	'MediaAgrupadaValidaInvestimentoPrecoVenda',
	'MediaAgrupadaValidaInvestimentoM2',
	'ValidaInvestimento',
	'Porcentagem',
	'PorcentagemTexto'}
    invs_col_donts = {  'AnuncioInfoPrecoIptuAnual',    'AnuncioAndarUnidade',     'AnuncioFacilidades','AnuncioUnidadesporAndar',     'PrecoAluguel',    'ContaIdentidadeNumero',     'TipoImovel',     'AnuncioBlocos',     'ContaEnderecoEntregaCep',     'AnuncioEnderecoNome',     'ValidaInvestimento',     'ContaEnderecoCobrancaZona',     'AnuncioInfoPrecoPrecodeAluguel',     'ContaEnderecoCobrancaEstado',    'ImovelNovoUsado',     'ContaEnderecoEntregaZona',     'Porcentagem',     'Possui Vaga',    'PrecoReais',  'ImovelNovoUsado',     'MedianaPrecoM2Rua',     'MedianaPrecoRelacoes',     'AnuncioInfoPrecoPrecoDeVenda'}
    invs_cols_clean = set(invs.columns).intersection(
    	set([*columns_invs])).difference(invs_col_donts)
    invs = invs[[*invs_cols_clean]].reset_index()
    invs['PrecoM2'] = invs['PrecoM2'].astype('int64')

    order_columns =['index',
                                'Bairro',
                                'PrecoVenda',
                                'PrecoM2',
                                'MediaM2',
                                'MedianaM2Relacoes',
                                'MediaPreco',
                                'MedianaBairroAreaTotal',
                                'MediaAgrupadaValidaInvestimentoPrecoVenda',
                                'PorcentagemTexto',
                                'AnuncioEnderecoRua',
                                'AreaUtil',
                                'AreaTotal',
                                'AnuncioQuartos',
                                'AnuncioSuites',
                                'AnuncioBanheiros',
                                'AnuncioVagasGaragem',
                                'AnuncioInfoPrecoValorCondominio',
                                'AnuncioTitulo',
                                'AnuncioExternoId',
                                'AnuncioDescricao',
                                'AnuncioEnderecoZona',
                                'AnuncioEnderecoBairro',
                                'AnuncioEnderecoRuaNumero',
                                'AnuncioEnderecoComplemento',
                                'AnuncioEnderecoCidade',
                                'AnuncioEnderecoEstado',
                                'AnuncioEnderecoCep',
                                'AnuncioDiasDesdeCriacaoCod',
                                'FinalidadeImovel',
                                'TipoAnunciante',
                                'ContaNome',
                                'ContaTelefoneCelular',
                                'AnuncioAnuncianteContatoTelefone',
                                'ContaTelefonePrincipal',
                                'ContaEmailPrincipal',
                                'ContaEnderecoCobrancaBairro',
                                'ContaEnderecoCobrancaRua',
                                'ContaEnderecoCobrancaRuaNumero',
                                'ContaEnderecoCobrancaComplemento',
                                'ContaEnderecoCobrancaCidade',
                                'ContaEnderecoCobrancaCep',
                                'ContaEnderecoEntregaBairro',
                                'ContaEnderecoEntregaRua',
                                'ContaEnderecoEntregaRuaNumero',
                                'ContaEnderecoEntregaComplemento',
                                'ContaEnderecoEntregaCidade',
                                'AnuncioCriadoEm',
                                'AnuncioAtualizadoEm',
                                'ContaSiteURL',
                                'LinkHref'
                                ]

    invs = invs[[i for i in order_columns if i in invs.columns]]

    invs = invs.rename(columns={'MediaAgrupadaValidaInvestimentoPrecoVenda':
                                                    'Preco Imoveis Similares',
                                                    'MediaAgrupadaValidaInvestimentoM2':
                                                    'Preco m2 Imoveis Similares', 'VagasBool': 'Possui Vaga','PorcentagemTexto': f'% preco/valor de mercado'})




    invs = invs.set_index('Bairro')
    invs.to_csv(f'invs_{time_today}_{zone}.csv', index=False)
    invs.to_excel(f'invs_{time_today}_{zone}.xlsx')






cc = dfs.groupby(["AnuncioEnderecoCep", "LatitudeLongitude", "Bairro"]).size()
cc = pd.DataFrame(cc).reset_index().sort_values(by=[0], ascending=False)

cep_lat_lon = {k: v for k, v in zip(cc['AnuncioEnderecoCep'], cc['LatitudeLongitude']) if k != None}
dfs.loc[dfs["LatitudeLongitude"].isna(), "LatitudeLongitude"] = dfs.loc[dfs["LatitudeLongitude"].isna(), "AnuncioEnderecoCep"].apply(lambda x: cep_lat_lon[x] if x in cep_lat_lon.keys() else None)
dfs.loc[dfs["AnuncioPortal"] == "OLX", "AreaTotal"] = dfs.loc[dfs["AreaTotal"].isnull(), "AreaUtil"].apply(lambda x: int(x))
dfs["PrecoVenda"] = dfs["PrecoVenda"].map(find_num)
dfs["AreaTotal"] = dfs["AreaTotal"].map(find_num)
dfs = dfs.loc[(dfs["PrecoVenda"] != None) & (dfs["PrecoVenda"] != 'None') & (dfs["PrecoVenda"] > 0) & (dfs["AreaTotal"] != None) & (dfs["AreaTotal"] != 'None') & (dfs["AreaTotal"] > 0), :]
dfs["PrecoVenda"] = dfs["PrecoVenda"].astype("int")
dfs["AreaTotal"] = dfs["AreaTotal"].astype("int")
dfs['PrecoM2'] = dfs['PrecoVenda'] / dfs['AreaTotal']
dfs.loc[(dfs["AnuncioPortal"] == "OLX") & (~dfs["LatitudeLongitude"].isna()), "AnuncioEnderecoLatitude"] = dfs.loc[(dfs["AnuncioPortal"] == "OLX") & (~dfs["LatitudeLongitude"].isna()), "LatitudeLongitude"].apply(lambda x: tuple(x[1: -1].split(", "))[0])
dfs.loc[(dfs["AnuncioPortal"] == "OLX") & (~dfs["LatitudeLongitude"].isna()), "AnuncioEnderecoLongitude"] = dfs.loc[(dfs["AnuncioPortal"] == "OLX") & (~dfs["LatitudeLongitude"].isna()), "LatitudeLongitude"].apply(lambda x: tuple(x[1: -1].split(", "))[1])
dfs["AnuncioEnderecoLatitude"] = dfs["AnuncioEnderecoLatitude"].astype("float")
dfs["AnuncioEnderecoLongitude"] = dfs["AnuncioEnderecoLongitude"].astype("float")
dfs = dfs.reindex()
dict_cluster = df_clusters_residential(dfs)
with concurrent.futures.ProcessPoolExecutor() as executor:
    dict_size = [executor.submit(df_clusters_size, dict_cluster[i]) for i in dict_cluster]
frames = []
for i in concurrent.futures.as_completed(dict_size):
    vc = yielder(i.result())
    for x in vc:
        frames.append(x)

frames = pd.concat(frames, ignore_index=True).reindex()
frames.drop_duplicates(subset = "LinkHref", inplace = True)
#call_invest(frames, 200000)




#for i in concurrent.futures.as_completed(dict_size)