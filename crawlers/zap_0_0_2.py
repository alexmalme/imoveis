#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 6:13:48 2019

@author: alx
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import time
from random import choice
from urllib.parse import quote
from urllib.parse import unquote


time_today = time.strftime("%Y_%m_%d_%H_%M")
timestamp = time.strftime("%Y%m%d%H%M")
delays = [1, 2, 3, 4, 5]

transacao = input('Escolha o tipo de transação: \n 1: Venda   2: Aluguel:')
if transacao.strip() == '1':
    transacao = 'venda'
elif transacao.strip() == '2':
    transacao = 'aluguel'
elif transacao.strip() not in ['1', '2']:
    continua = True
    while continua:
        transacao = input(
            'Escolha o tipo de transação: \n 1: Venda   2: Aluguel: ')
        if transacao.strip() == '1':
            transacao = 'venda'
            continua = False
        elif transacao.strip() == '2':
            transacao = 'aluguel'
            continua = False
print(transacao)
state = input('Escolha o Estado: \n1: RJ  2: SP ')
while state.strip() not in ['1', '2']:
    print('Você não escolheu um Estado válido')
    state = input('Escolha o Estado: \n1: RJ  2: SP ')
if state.strip() == '1':
    state = 'rj'
elif state.strip() == '2':
    state = 'sp'
print('Você escolheu:', str(state))
city = input('Escolha a Cidade: \n1: Rio de Janeiro  2: São Paulo ')
while city.strip() not in ['1', '2']:
    print('Você não escolheu uma city válida')
    city = input('Escolha a Cidade: \n1: Rio de Janeiro  2: São Paulo ')
if city.strip() == '1':
    city = 'rio-de-janeiro'
elif city.strip() == '2':
    city = 'sao-paulo'
print('Você escolheu:', str(city))
zone = input(
    'Escolha a zona: \n1: Zona Sul  2: Zona Oeste  3: Zona Norte   4: Zona Central')
while zone.strip() not in ['1', '2', '3', '4']:
    print('Você não escolheu uma Zona valida')
    zone = input(
        'Escolha a zona: \n1: Zona Sul  2: Zona Oeste  3: Zona Norte   4: Zona Central')
if zone.strip() == '1':
    zone = 'zona-sul'
elif zone.strip() == '2':
    zone = 'zona-oeste'
elif zone.strip() == '3':
    zone = 'zona-norte'
elif zone.strip() == '4':
    zone = 'zona-central'

# TODO Escrever os caminhos dos arquivos
# file = str(
#    f'/home/alx_malme/imoveis/zaps_down/zap_{state}_{city}_{zone}_{time_today}')
# file_log_erro_ = str(
#    f'/home/alx_malme/imoveis/zaps_down/logs/log_erro_zap_{state}_{city}_{zone}_{time_today}')


class ZapMining:

    def __init__(
        self,
        transacao=transacao,
        zone=zone,
        file=file,
        state=state,
        city=city,
        pagina=1,
        ordem='Valor',
        start_url='view-source:https://www.zapimoveis.com.br'
    ):
        self.transacao = transacao
        self.state = state
        self.city = city
        self.zone = zone
        self.pagina = pagina
        self.ordem = ordem
        self.start_url = start_url
        self.file = file

    def driver_(self):
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        return driver

    def url_gen(self, num_pagina):
        pagina = str(num_pagina)
        state_ = str(self.state).lower()
        state_ = quote(state_)
        print(state_)
        city_ = str(self.city).replace(" ", "-").lower()
        city_ = quote(city_)
        print(city_)
        zone_ = str(self.zone).replace(' ', '-')
        zone_ = quote(zone_)
        print(zone_)
        ordem_ = str(self.ordem).title()
        ordem_ = quote(ordem_)
        print(ordem_)
        transacao = str(self.transacao).lower()
        start_url = str(self.start_url)
        url = (f"{start_url}/{transacao}/imoveis/{state_}+"
               f"{city_}+{zone_}/?pagina={pagina}&transacao={(transacao).title()}&ordem={ordem_}"
               )
        return url

    def start_page_url(self, number=1):
        first_pg_url = self.url_gen(number)
        return str(first_pg_url)

    def page_count(self, page_source):
        '''Retorna o número total de páginas encontradas com a busca feita.
        O Zap não mostra no seu front-end quantas páginas existem para a busca feita.
        Essa função serve como auxílio nas divisões ou filtros a serem usados, 
        já que o ZAP não retorna páginas à partir da página 247.'''
        rex = re.compile(r'\"pagination\".*\"listingsSize\"\:(\d+)')
        pg_count = int(rex.search(page_source).group(1))
        return pg_count

    def page_counter(self, url_page_source):
        driver = self.driver_()
        url = url_page_source
        driver.get(url)
        pagina = driver.page_source
        delay = choice(delays)
        time.sleep(delay)
        driver.close()
        # print(pagina)
        counted = int(self.page_count(str(pagina)))
        return counted

    def total_pages(self):
        driver = self.driver_()
        url = str(self.start_page_url())
        driver.get(url)
        pagina = driver.page_source
        delay = choice(delays)
        time.sleep(delay)
        driver.close()
        counted = int(self.page_count(str(pagina)))
        return counted

    def info_text_save(self, pag):
        rex = re.compile(
            r'\"results\"\:\{\"listings\"\:\[(.*"videos.*\]),\"filters\"')
        rox = re.compile(r'\"pagination\".*\"currentPage\"\:(\d+)')
        re_url = re.compile(r'<title>(.*)<\/title>')
        url_ = re_url.search(pag).group(1)
        un_url = unquote(url_)
        try:
            actual_page = int(rox.search(pag).group(1))
            achar = rex.search(pag).group(1)
            f = open(self.file, 'a+')
            f.write(str(achar))
            f.close()
            print("escrevi a pagina: " + str(actual_page) + '\n')
        except:
            print('**************************')
            print('Não consegui pegar o texto da pag: ' + str(un_url))
            print('**************************')
            with open(file_log_erro_, 'a+') as logerro:
                escrever_log = logerro.write(str("ERRO NA PÁGINA: ") + un_url)
            escrever_log

    def pega_zap(self, get_url):
        driver = self.driver_()
        try:
            driver.get(get_url)
            pagina = driver.page_source
            delay = choice(delays)
            time.sleep(delay)
            driver.close()
            self.info_text_save(pagina)
        except:
            driver.close()
            with open(file_log_erro_, 'a+') as logerro:
                escrever_log = logerro.write(f"ERRO NA PÁGINA: {get_url}")
            escrever_log

    def minus_one(self, x):
        x = int(x) - 1
        return x

    def separa_paginas(self, args):
        rex = re.compile(r'(.*pagina=)(\d+)(.*)')
        key_page = str(args[0])
        value_total_pages = str(args[1])
        pre_page = rex.search(key_page).group(1)
        #page_ = rex.search(key_page).group(2)
        end_page = rex.search(key_page).group(3)
        unpack_paginas = [
            pre_page + str(i) + end_page for i in range(1, int(int(value_total_pages) + 1))]
        [self.pega_zap(i) for i in unpack_paginas]

    def last_price(self, pag):
        rex = re.compile(r'(?<=\"salePrice\"\:\"R\$\s)([0-9.]*)')
        precos = rex.findall(pag)
        if precos:
            ultimo_preco = precos[-1]
            preco = ''.join(i for i in ultimo_preco if i.isnumeric())
            return preco

    def muitas_paginas(self,
                       numero_de_imoveis_total,
                       preco_minimo=100000,
                       preco_maximo_total=0):
        '''
        Função para criar um dicionário ordenado com as páginas a serem baixadas.
        Ele retornará a página inicial dos imóveis de menor Valor
        e a página final com o maior valor.
        Olhar o preço mínimo, pois não faz sentido usar "0" como valor de compra de um 
        imóvel.
        '''
        dic_urls = {}
        if preco_maximo_total == 0:
            preco_maximo = ''
        else:
            preco_maximo = '&precoMaximo=' + str(preco_maximo_total)
        preco_minimo = str(preco_minimo)
        # a variável abaixo é o número total de páginas encontradas para a url passada
        # na função divide_to_win
        numero_de_imoveis_iterar = int(numero_de_imoveis_total)
        numero_de_paginas_iterar = round(numero_de_imoveis_iterar / 36)
        print(
            f'Esse é o nº de imóveis para iterar: {numero_de_imoveis_iterar}')
        print(
            f'Esse é o nº de páginas para iterar: {numero_de_paginas_iterar}\n')
        index_total = 0
        while numero_de_paginas_iterar >= 0:
            # index_page = página dentro dos valores selecionados
            url_init = self.url_gen(1)
            u = url_init + '&precoMinimo=' + preco_minimo + preco_maximo
            driver = self.driver_()
            driver.get(u)
            cod_fonte = driver.page_source
            driver.close()
            numero_de_imoveis_iterar = self.page_count(cod_fonte)
            numero_de_paginas_iterar = round(numero_de_imoveis_iterar / 36)
            range_last_page = 241 if numero_de_paginas_iterar >= 241 else numero_de_paginas_iterar
            print(f'O range_last_page é {range_last_page}\n')
            for index_page in range(1, range_last_page):
                # index_total = página dentro do total de páginas
                index_total += 1
                print(f'Index = {index_total}\n')
                url = self.url_gen(index_page)
                u = url + '&precoMinimo=' + preco_minimo + preco_maximo
                print(f'u = {u}')
                dic_urls.setdefault(u, [index_page, index_total])
            driver = self.driver_()
            driver.get(u)
            cod_fonte = driver.page_source
            driver.close()
            preco_minimo = self.last_price(cod_fonte)
            print(f'Novo preço mínimo = {preco_minimo}')
            numero_de_paginas_iterar -= index_page
            print(
                f'Número de páginas que faltam para iterar = {numero_de_paginas_iterar}')
        with open(f"{state}_{city}_{zone}_{time_today}", "a+") as endereco_file:
            endereco_file.write(str(dic_urls))
        return dic_urls

    def divide_to_win(self, start_url=start_page_url):
        driver = self.driver_()
        driver.get(str(start_url))
        pagina = driver.page_source
        driver.close()
        conta_paginas = self.page_count(pagina)
        if int(conta_paginas) >= 260:
            conta_paginas = int(conta_paginas)
            dicio_pags = self.muitas_paginas(conta_paginas, 150000)
            [self.pega_zap(item) for item in dicio_pags.keys()]
        else:
            unpack_paginas = [self.url_gen(i)
                              for i in range(1, int(conta_paginas + 1))]
            [self.pega_zap(i) for i in unpack_paginas]


def main():
    zap = ZapMining()
    # gerar 1a url
    first_url = zap.start_page_url(1)
    print(first_url)
    miner = zap.divide_to_win(first_url)
    miner
    print('terminado')


if __name__ == "__main__":
    main()
