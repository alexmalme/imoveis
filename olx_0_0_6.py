# %%
import sqlite3
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import time
from urllib.parse import unquote
import json


# %%
class Parametros:
    def __init__(
        self,
        state,
        start_url,
        city,
        zona,
        transacao,
        preco_minimo,
        preco_maximo,
        ordem,
        pagina
    ):
        """
        Args:
            state ([string]): estado. ex: sp
            start_url ([string]): ex: olx.com.br
            city ([string]): cidade. ex: sao-paulo
            zona ([string]): ex: zona-sul
            transacao ([string]): venda ou aluguel
            preco_minimo ([string]): recebe no formato '&ps=' + numeral,
                                     ex: &ps=100000
            preco_maximo ([string]): recebe no formato '&pe=' + numeral,
                                     ex: &pe=100000
            ordem ([string]): ordem dos resultados. 'preco': 'sp=1',
                              'mais novos': 'sf=1' e 'mais relevantes': ''
            pagina ([string]): nº da página inicial. recebe no formato
                               '&o=1'
        """
        self.state = state
        self.start_url = start_url
        self.city = city
        self.zona = zona
        self.transacao = transacao
        self.preco_minimo = (
            str(preco_minimo) if str(preco_minimo) is not None else ''
        )
        self.preco_maximo = (
            str(preco_maximo) if str(preco_maximo) is not None else ''
        )
        self.ordem = ordem
        self.pagina = (
            str(pagina) if str(pagina) not in [None, ''] else '1'
        )
        self.url_compacto = (
            f'https://{self.get_state}'
            f'.{self.get_start_url}/'
            f'{self.get_city}-e-regiao/'
            if self.get_city is not None
            else
            f'https://{self.get_state}'
            f'.{self.get_start_url}/'
        )
        self.url_default = (
            f"{self.get_url_compacto}"
            f"{self.get_zona}/imoveis/"
            f"{self.get_transacao}"
            f"{self.get_ordem}"
            f"{self.get_preco_minimo}"
            f"{self.get_preco_maximo}"
            f"{self.get_pagina}"
        )

    @property
    def get_url_compacto(self):
        return self.url_compacto

    @property
    def get_url_default(self):
        return self.url_default

    def set_url_default(
        self,
        url_compacto=None,
        zona=None,
        transacao=None,
        ordem=None,
        preco_minimo=None,
        preco_maximo=None,
        pagina=None
    ):
        u_compacto = (
            url_compacto if url_compacto is not None else self.get_url_compacto
        )
        z = zona if zona is not None else self.get_zona
        t = transacao if transacao is not None else self.get_transacao
        o = ordem if ordem is not None else self.get_ordem
        p_min = preco_minimo if preco_minimo is not None else self.get_preco_minimo
        p_max = preco_maximo if preco_maximo is not None else self.get_preco_maximo
        pg = pagina if pagina is not None else self.get_pagina
        self.url_default = f"{u_compacto}{z}/imoveis/{t}{o}{p_min}{p_max}{pg}"

    @property
    def get_state(self):
        return self.state

    @get_state.setter
    def get_state(self, newstate):
        self.state = newstate

    @property
    def get_start_url(self):
        return self.start_url

    @get_start_url.setter
    def get_start_url(self, newstart_url):
        self.start_url = newstart_url

    @property
    def get_city(self):
        return self.city

    @get_city.setter
    def get_city(self, newcity):
        self.city = newcity

    @property
    def get_zona(self):
        return self.zona

    @get_zona.setter
    def get_zona(self, newzona):
        self.zona = newzona

    @property
    def get_transacao(self):
        return self.transacao

    @get_transacao.setter
    def get_transacao(self, newtransacao):
        self.transacao = newtransacao + '?'

    @property
    def get_preco_minimo(self):
        return self.preco_minimo

    @get_preco_minimo.setter
    def get_preco_minimo(self, newpreco_minimo):
        self.preco_minimo = (f'&ps={newpreco_minimo}')

    @property
    def get_preco_maximo(self):
        return self.preco_maximo

    @get_preco_maximo.setter
    def get_preco_maximo(self, newpreco_maximo):
        self.preco_maximo = (f'&pe={newpreco_maximo}')

    @property
    def get_ordem(self):
        return self.ordem

    @get_ordem.setter
    def get_ordem(self, newordem):
        """
        Preço: 'sp=1',
        Mais Recentes: 'sf=1',
        Mais Relevantes: ''
        """
        self.ordem = newordem

    @property
    def get_pagina(self):
        return self.pagina

    @get_pagina.setter
    def get_pagina(self, newpagina):
        self.pagina = (f'&o={newpagina}')

# %%
    def choose_transacao(self):
        """
        Função para escolha do tipo de transação.
        Recebe input do usuário
        Altera o self.get_transacao
        """
        transacao = input(
            f'Escolha o tipo de transação: \n'
            f'1: Venda   2: Aluguel: '
        )
        if transacao.strip() == '1':
            transacao = 'venda'
        elif transacao.strip() == '2':
            transacao = 'aluguel'
        elif transacao.strip() not in ['1', '2']:
            continua = True
            while continua:
                transacao = input(
                    f'Escolha o tipo de transação: \n'
                    f'1: Venda 2: Aluguel: '
                )
                if transacao.strip() == '1':
                    transacao = 'venda'
                    continua = False
                elif transacao.strip() == '2':
                    transacao = 'aluguel'
                    continua = False
        print(transacao)
        self.get_transacao = transacao

# %%
    def choose_state(self):
        """
        Função para escolha do estado.
        Recebe input do usuário
        Altera o self.get_state
        """
        state = input(
            f'Escolha o Estado: \n'
            f'1: RJ  2: SP '
        )
        while state.strip() not in ['1', '2']:
            print('Você não escolheu um Estado válido')
            state = input(
                f'Escolha o Estado: \n'
                f'1: RJ  2: SP '
            )
        if state.strip() == '1':
            state = 'rj'
        elif state.strip() == '2':
            state = 'sp'
        print('Você escolheu:', str(state))
        self.get_state = state

# %%
    def choose_city(self):
        """
        Função para escolha da cidade
        Recebe input do usuário
        Altera o self.get_city.
        """
        city = input(
            f'Escolha a Cidade: \n'
            f'1: Rio de Janeiro  2: São Paulo '
        )
        while city.strip() not in ['1', '2']:
            print('Você não escolheu uma city válida')
            city = input(
                f'Escolha a Cidade: \n'
                f'1: Rio de Janeiro  2: São Paulo '
            )
        if city.strip() == '1':
            city = 'rio-de-janeiro'
        elif city.strip() == '2':
            city = 'sao-paulo'
        print('Você escolheu:', str(city))
        self.get_city = city

# %%
    def choose_zona(self):
        """
        Função para escolha da zona
        Recebe input do usuário
        Altera o self.get_zona.
        """

        zone = input(
            f'Escolha a zona: \n'
            f'1: Zona Sul  2: Zona Oeste  3: Zona Norte   4: Zona Central'
        )
        while zone.strip() not in ['1', '2', '3', '4']:
            print('Você não escolheu uma Zona valida')
            zone = input(
                f'Escolha a zona: \n'
                f'1: Zona Sul  2: Zona Oeste  3: Zona Norte   4: Zona Central'
            )
        if zone.strip() == '1':
            zone = 'zona-sul'
        elif zone.strip() == '2':
            zone = 'zona-oeste'
        elif zone.strip() == '3':
            zone = 'zona-norte'
        elif zone.strip() == '4':
            zone = 'zona-central'
        self.get_zona = zone

# %%
    def choose_ordem(self):
        """
        Função para escolha da ordem dos resultados
        Recebe input do usuário
        Altera o self.get_ordem.
        """
        ordem = input(
            f'Escolha a ordem: \n'
            f'Preço: 1, Mais Recentes: 2, Mais Relevantes: 3 '
        )
        while ordem.strip() not in ['1', '2', '3']:
            print('Você não escolheu uma ordem válida')
            ordem = input(
                f'Escolha a ordem: \n'
                f'Preço: 1, Mais Recentes: 2, Mais Relevantes: 3 '
            )
        if ordem.strip() == '1':
            ordem = 'sp=1'
        elif ordem.strip() == '2':
            ordem = 'sf=1'
        elif ordem.strip() == '3':
            ordem = ''
        self.get_ordem = ordem

# %%
    def choose_pagina(self):
        """
        Função para escolha da página
        Recebe input do usuário
        Altera o self.get_pagina.
        """
        pagina = input("""
        Digite a pagina inicial da pesquisa.
        Use de 1-100\nDefault: 1
        """)
        pagina = ''.join(i for i in pagina if i.isnumeric())
        if pagina in ['', None]:
            pagina = '1'
        self.get_pagina = pagina

# %%
    def choose_preco_minimo(self):
        """
        Função para escolha do preço mínimo
        Recebe input do usuário
        Não envia o &ps= para formatação, essa alteração já é realizada no setter
        Altera o self.get_preco_minimo.
        """
        preco_minimo = input(
            'Digite o preço mínimo. Use apenas números: '
        )
        if preco_minimo in ['', None]:
            preco_minimo = '0'
        preco_minimo = ''.join(i for i in preco_minimo if i.isnumeric())
        self.get_preco_minimo = preco_minimo

# %%
    def choose_preco_maximo(self):
        """
        Função para escolha do preço máximo
        Recebe input do usuário
        Não envia o &pe= para formatação, essa alteração já é realizada no setter
        Altera o self.get_preco_maximo.
        """
        preco_maximo = input(
            '''Digite o preço maximo.
            Use apenas números ou aperte enter para não escolher valor limite: '''
        )
        while (
            len(preco_maximo) > 1 and int(
                preco_maximo) < int(self.get_preco_minimo)
        ):
            preco_maximo = input(
                """O preço máximo digitado é menor que o preço mínimo.
                Digite o preço maximo. Use apenas números: """
            )
        if preco_maximo in ['0', None, '']:
            preco_maximo = ''
        preco_maximo = ''.join(i for i in preco_maximo if i.isnumeric())
        self.get_preco_maximo = preco_maximo

# %%
    def escolhe_link(self):
        """
        Função que chama as funções de criação do url
        Criada para organização das chamadas.
        """
        self.choose_transacao()
        self.choose_state()
        self.choose_city()
        self.choose_zona()
        self.choose_ordem()
        self.choose_pagina()
        self.choose_preco_minimo()
        self.set_url_default()

# %%
    def pergunta_inicial(self):
        """
        Primeira função que aparece para o usuário
        Se o input for 'S', ela ira chamar a função 'escolhe_link', que é
        uma função construtora.
        """
        link_inicial = input(
            f'Deseja iniciar a pesquisa no OLX'
            f'com o link padrão:\n {self.get_url_default} (S/N) '
        )
        if link_inicial.lower().strip() in ['não', 'n', 'nao']:
            print(
                'Escolha os dados para construção do link inicial'
            )
            self.escolhe_link()

# %%
class Urls(Parametros):

    def __init__(
        self,
        state,
        start_url,
        city,
        zona,
        transacao,
        preco_minimo,
        preco_maximo,
        ordem,
        pagina
    ):
        """
        Igual ao __init__ da classe Parametros
        """
        self.state = state
        self.start_url = start_url
        self.city = city
        self.zona = zona
        self.transacao = transacao
        self.preco_minimo = (
            str(preco_minimo) if str(preco_minimo) is not None else ''
        )
        self.preco_maximo = (
            str(preco_maximo) if str(preco_maximo) is not None else ''
        )
        self.ordem = ordem
        self.pagina = str(pagina) if str(pagina) not in [None, ''] else '1'
        super().__init__(state, start_url, city, zona, transacao, preco_minimo,
                         preco_maximo, ordem, pagina)
        self.url_completo = super().get_url_default

    @property
    def get_url_completo(self):
        return self.url_completo

    def gen_url_completo(self,
                         url_compacto,
                         zona,
                         transacao,
                         ordem,
                         preco_minimo,
                         preco_maximo,
                         pagina
                         ):
        """Recebe os parâmetros e retorna uma nova url
        Altera o valor do self.url_completo
            url_compacto ([string])
            zona ([string]): ex: zona-sul
            transacao ([string]): venda ou aluguel
            ordem ([string]): ordem dos resultados. 'preco': 'sp=1',
                              'mais novos': 'sf=1' e 'mais relevantes': ''
            preco_minimo ([string]): recebe no formato '&ps=' + numeral,
                                     ex: &ps=100000
            preco_maximo ([string]): recebe no formato '&pe=' + numeral,
                                     ex: &pe=100000
            pagina ([string]): nº da página inicial. recebe no formato
                               '&o=1'.
        """
        self.url_completo = (
            f"{url_compacto}"
            f"{zona}/imoveis/"
            f"{transacao}"
            f"{ordem}"
            f"{preco_minimo}"
            f"{preco_maximo}"
            f"{pagina}"
        )

    def set_url_completo(self,
                         url_compacto='',
                         zona='',
                         transacao='venda?',
                         ordem='sp=1',
                         preco_minimo='',
                         preco_maximo='',
                         pagina=''
                         ):
        """
        Recebe e limpa os valores para a criação do url_completo
        Chama o self.gen_url_completo

            Args:
            url_compacto (str, optional):  Defaults to ''.
            zona (str, optional):  Defaults to ''.
            transacao (str, optional):  Defaults to 'venda?'.
            ordem (str, optional):  Defaults to 'sp=1'.
            preco_minimo (str, optional):  Defaults to ''.
            preco_maximo (str, optional):  Defaults to ''.
            pagina (str, optional):  Defaults to ''.
        """
        u_compacto = url_compacto if url_compacto != '' else self.url_compacto
        z = zona if zona != '' else self.zona
        t = transacao if transacao != '' else self.transacao
        o = ordem if ordem != '' else self.ordem
        p_min = preco_minimo if preco_minimo != '' else self.preco_minimo
        p_max = preco_maximo if preco_maximo != '' else self.preco_maximo
        pg = pagina if pagina != '' else self.pagina
        return self.gen_url_completo(u_compacto, z, t, o, p_min, p_max, pg)

    @staticmethod
    def get_time_today():
        """
        Função criada para acrescentar a data do dia em:
        Coluna Data da captura
        Nome dos arquivos salvos com a data da sua criação
        Returns:
            string: no formato '2020_11_05_22_31' (exemplo)
        """
        time_today = time.strftime("%Y_%m_%d_%H_%M")
        return time_today

# %%
    def quantos_faltam(self, r):
        rt = r.text.split()
        qts = sorted(
            {int(it.replace('.', ''))
             for it in rt
             for t in it if t.isnumeric()}
        )
        return qts

# %%
    def parse(self, url_completo, url_compacto, count=0):
        print('-' * 30)
        print(url_completo)
        print('-' * 30, '\n' * 2)
        driver = self.driver_()
        driver.get(url_completo)
        items = driver.find_elements_by_xpath(
            '//ul[@id="ad-list"]//a[not(contains(@class, "OLXad-list-link"))]'
        )
        sql, PrecoVenda = None, None
        for item in items:
            if url_compacto in item.get_attribute('href'):
                url_pag = 'view-source:' + item.get_attribute('href')
                print(url_pag)
                # colher os detalhes de cada imóvel
                sql = self.parse_detail(url_pag)
                # salvar no banco de dados
                if sql:
                    self.process_item(sql)
                    PrecoVenda = sql['PrecoVenda']
        try:
            next_page = driver.find_element_by_xpath(
                '//a[@data-lurker-detail="next_page"]').get_attribute('href')
        except:
            next_page = None
            print('-' * 30)
            print(f"Última página é {url_completo}")
            print('-' * 30)
        if next_page:
            print('-' * 50)
            print(f"Próxima página {next_page}")
            print('-' * 50)
            driver.close()
            return self.parse(next_page, url_compacto, count=0)
        else:
            # contagem de quantos imóveis faltam no total
            try:
                r = driver.find_element_by_xpath(
                    '/html/body/div[1]/div[2]/div[1]/div[4]/div/div[2]/div[3]/div/span'
                )
            except:
                pass
            try:
                r = driver.find_element_by_xpath(
                    '/html/body/div[1]/div[2]/div[2]/div/div[2]/div[2]/div/div[8]/div/span'
                )
            except:
                r = None
            finally:
                if r is not None:
                    vals = self.quantos_faltam(r)
                    if vals[-1] - vals[-2] <= 50:
                        print("Terminei tudo")
                        driver.close()
                    else:
                        # encontrar o último preço encontrado e colocar ele como preço mínimo
                        if sql:
                            ui = self.get_url_completo
                            print(f'Esse é o preço mínimo: {PrecoVenda}')
                            print(
                                f'Esse é o get self.get_preco_minimo'
                                f'{self.get_preco_minimo}'
                            )
                            print(f'Esse é o ui: {ui}')
                            preco_mininmo = '&ps=' + str(PrecoVenda)
                            self.set_url_completo(
                                preco_minimo=preco_mininmo, pagina='&o=1')
                            print('Olá')
                            print(self.url_completo)
                            driver.close()
                            return self.parse(self.get_url_completo, self.get_url_compacto)
                        else:
                            driver.close()
                            print(
                                'Deu erro na hora de pegar quantos faltam para recomeçar'
                            )
                else:
                    print('r = None')
                    driver.close()
                    if count >= 3:
                        print(
                            'Estou encerrando o programa sem saber para onde ir'
                        )
                    else:
                        return self.parse(url_completo, url_compacto, count + 1)

# %%
    def driver_(self):
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
#       driver = webdriver.Firefox()
        return driver

# %%
    def fnan(self, v):
        try:
            val = v
        except:
            val = ''
        return val

# %%
    def cod_anuncio(self, text):
        rex = re.compile(r'Código do anúncio\: (.*)\.')
        try:
            cods = rex.search(str(text).replace('&lt;br&gt;', '')).group(1)
        except:
            cods = ''
        return cods

# %%
    def find_num(self, palavra):
        rex = re.compile(r'(\d+)')
        try:
            w = rex.search(str(palavra)).group(1)
        except:
            w = 0
        return int(w)

# %%
    def parse_detail(self, url):
        try:
            driver = self.driver_()
            driver.get(url)
            pagina = driver.page_source
            driver.close()
            rex = re.compile(r'window\.dataLayer = (.*}}])')
            ver = rex.search(pagina).group(1)
            rox = re.compile(r'data-json(.*),.*securityTips')
            tao = rox.search(unquote(pagina)).group(1)
            t = (
                tao.replace('</span>', '')
                .replace('<a class="attribute-value">', '')
                .replace('<span class="entity">', '')
                .replace('<span>', '')
                .replace('&amp;', '&')
                .replace('&quot;', '"')
            )
            fields = json.loads(t[2:] + '}}')
            dicionario = json.loads(ver[1:-1])
            LinkHref = self.fnan(fields['ad']['friendlyUrl'])
            AnuncioEnderecoBairro = self.fnan(
                fields['ad']['location']['neighbourhood']
            )
            AnuncioEnderecoRua = self.fnan(fields['ad']['location']['address'])
            AnuncioTitulo = self.fnan(fields['ad']['subject'])
            PrecoReais = self.fnan(fields['ad']['priceValue'])
            PrecoAntigo = self.fnan(fields['ad']['oldPrice'])
            PrecoVenda = self.fnan(
                (str(
                    fields['ad']['priceValue']
                )
                    .replace('R$ ', '')
                )
                .replace('.', '')
            )
            ContaNome = self.fnan(fields['ad']['user']['name'])
            AnuncioAnuncianteContatoTelefone = self.fnan(
                fields['ad']['phone']['phone']
            )
            AnuncioDescricao = self.fnan(
                (
                    fields['ad']['body']
                )
                .replace('&lt;br&gt;', '. ')
            )
            AnuncioUnidadeTipos = (
                self.fnan(
                    (
                        dicionario['page']['adDetail']['category']
                    ).lower()
                )
                .replace('apartamentos', 'apartamento')
                .replace('casas', 'casa')
            )
            AnuncioQuartos = (
                self.find_num(
                    [fields['ad']['properties'][i]['value']
                     for i, val
                     in enumerate(fields['ad']['properties'])
                     if val['name'] == 'rooms'][0]
                )
                if [fields['ad']['properties'][i]['value']
                    for i, val
                    in enumerate(fields['ad']['properties'])
                    if val['name'] == 'rooms'] != [] else 0
            )
            AnuncioBanheiros = (
                self.find_num(
                    [fields['ad']['properties'][i]['value']
                     for i, val
                     in enumerate(fields['ad']['properties'])
                     if val['name'] == 'bathrooms'][0]
                )
                if [fields['ad']['properties'][i]['value']
                    for i, val
                    in enumerate(fields['ad']['properties'])
                    if val['name'] == 'bathrooms'] != [] else 0
            )
            AnuncioVagasGaragem = (
                self.find_num(
                    [fields['ad']['properties'][i]['value']
                     for i, val
                     in enumerate(fields['ad']['properties'])
                     if val['name'] == 'garage_spaces'][0]
                )
                if [fields['ad']['properties'][i]['value']
                    for i, val
                    in enumerate(fields['ad']['properties'])
                    if val['name'] == 'garage_spaces'] != [] else 0
            )
            AreaUtil = (
                self.find_num(
                    [fields['ad']['properties'][i]['value']
                     for i, val
                     in enumerate(fields['ad']['properties'])
                     if val['name'] == 'size'][0]
                )
                if [fields['ad']['properties'][i]['value']
                    for i, val
                    in enumerate(fields['ad']['properties'])
                    if val['name'] == 'size'] != [] else 0
            )
            AnuncioInfoPrecoValorCondominio = (
                self.fnan(
                    [fields['ad']['properties'][i]['value']
                     for i, val
                     in enumerate(fields['ad']['properties'])
                     if val['name'] == 'condominio'][0])
                if [fields['ad']['properties'][i]['value']
                    for i, val
                    in enumerate(fields['ad']['properties'])
                    if val['name'] == 'condominio'] != [] else 0
            )
            AnuncioInfoPrecoIptuAnual = (
                self.fnan([fields['ad']['properties'][i]['value']
                           for i, val
                           in enumerate(fields['ad']['properties'])
                           if val['name'] == 'iptu'][0])
                if [fields['ad']['properties'][i]['value']
                    for i, val
                    in enumerate(fields['ad']['properties'])
                    if val['name'] == 'iptu'] != [] else 0
            )
            AnuncioEnderecoCep = self.fnan(fields['ad']['location']['zipcode'])
            AnuncioEnderecoCidade = self.fnan(
                fields['ad']['location']['municipality']
            )
            AnuncioDataCaptura = self.get_time_today()
            AnuncioEnderecoZona = self.fnan(
                (fields['ad']['location']['zone']).replace('-', ' ').title()
            )
            AnuncioEnderecoEstado = (
                'Rio de Janeiro'
                if fields['ad']['location']['uf'] == 'RJ'
                else fields['ad']['location']['uf']
            )
            AnuncioSubTitulo = self.fnan(
                dicionario['page']['adDetail']['real_estate_type']
            )
            AnuncioExternoId = self.fnan(
                self.cod_anuncio(fields['ad']['body'])
            )
            AnuncioEnderecoLatitude = self.fnan(
                fields['ad']['location']['mapLati']
            )
            AnuncioEnderecoLongitude = self.fnan(
                fields['ad']['location']['mapLong']
            )
            TipoAnunciante = (
                'proprietario'
                if fields['ad']['professionalAd'] is False
                else 'profissional'
            )
            AnuncioPortal = 'OLX'
            VagasBool = (
                1
                if (AnuncioVagasGaragem > 0 and AnuncioVagasGaragem == '')
                else 0
            )
            AnuncioCriadoEm = self.fnan(
                (fields['ad']['listTime']).replace('T', ' ').replace('Z', '')
            )

            item = {
                "LinkHref": LinkHref,
                "AnuncioEnderecoBairro": AnuncioEnderecoBairro,
                "AnuncioEnderecoRua": AnuncioEnderecoRua,
                "AnuncioTitulo": AnuncioTitulo,
                "PrecoReais": PrecoReais,
                "PrecoAntigo": PrecoAntigo,
                "PrecoVenda": PrecoVenda,
                "ContaNome": ContaNome,
                "AnuncioAnuncianteContatoTelefone": AnuncioAnuncianteContatoTelefone,
                "AnuncioDescricao": AnuncioDescricao,
                "AnuncioUnidadeTipos": AnuncioUnidadeTipos,
                "AnuncioQuartos": AnuncioQuartos,
                "AnuncioBanheiros": AnuncioBanheiros,
                "AnuncioVagasGaragem": AnuncioVagasGaragem,
                "AreaUtil": AreaUtil,
                "AnuncioInfoPrecoValorCondominio": AnuncioInfoPrecoValorCondominio,
                "AnuncioInfoPrecoIptuAnual": AnuncioInfoPrecoIptuAnual,
                "AnuncioEnderecoCep": AnuncioEnderecoCep,
                "AnuncioEnderecoCidade": AnuncioEnderecoCidade,
                "AnuncioDataCaptura": AnuncioDataCaptura,
                "AnuncioEnderecoZona": AnuncioEnderecoZona,
                "AnuncioEnderecoEstado": AnuncioEnderecoEstado,
                "AnuncioSubTitulo": AnuncioSubTitulo,
                "AnuncioExternoId": AnuncioExternoId,
                "AnuncioEnderecoLatitude": AnuncioEnderecoLatitude,
                "AnuncioEnderecoLongitude": AnuncioEnderecoLongitude,
                "TipoAnunciante": TipoAnunciante,
                "AnuncioPortal": AnuncioPortal,
                "VagasBool": VagasBool,
                "AnuncioCriadoEm": AnuncioCriadoEm
            }
            print(item)
            return item
        except:
            print('Deu Erro')
            return None

# %%
    def process_item(self, item):
        conn = sqlite3.connect('/home/alx_malme/imoveis/db/todos_imoveis.db')
        conn.execute('''insert into inbox (
            LinkHref,
            AnuncioEnderecoBairro,
            AnuncioEnderecoRua,
            AnuncioTitulo,
            PrecoReais,
            PrecoAntigo,
            PrecoVenda,
            AnuncioAnuncianteContatoTelefone,
            ContaNome,
            AnuncioDescricao,
            AnuncioUnidadeTipos,
            AnuncioQuartos,
            AnuncioBanheiros,
            AnuncioVagasGaragem,
            AreaUtil,
            AnuncioInfoPrecoValorCondominio,
            AnuncioEnderecoCep,
            AnuncioInfoPrecoIptuAnual,
            AnuncioEnderecoCidade,
            AnuncioDataCaptura,
            AnuncioEnderecoZona,
            AnuncioEnderecoEstado,
            AnuncioSubTitulo,
            AnuncioExternoId,
            AnuncioEnderecoLatitude,
            AnuncioEnderecoLongitude,
            TipoAnunciante,
            AnuncioPortal,
            VagasBool,
            AnuncioCriadoEm
        )
        values
        (
            :LinkHref,
            :AnuncioEnderecoBairro,
            :AnuncioEnderecoRua,
            :AnuncioTitulo,
            :PrecoReais,
            :PrecoAntigo,
            :PrecoVenda,
            :AnuncioAnuncianteContatoTelefone,
            :ContaNome,
            :AnuncioDescricao,
            :AnuncioUnidadeTipos,
            :AnuncioQuartos,
            :AnuncioBanheiros,
            :AnuncioVagasGaragem,
            :AreaUtil,
            :AnuncioInfoPrecoValorCondominio,
            :AnuncioEnderecoCep,
            :AnuncioInfoPrecoIptuAnual,
            :AnuncioEnderecoCidade,
            :AnuncioDataCaptura,
            :AnuncioEnderecoZona,
            :AnuncioEnderecoEstado,
            :AnuncioSubTitulo,
            :AnuncioExternoId,
            :AnuncioEnderecoLatitude,
            :AnuncioEnderecoLongitude,
            :TipoAnunciante,
            :AnuncioPortal,
            :VagasBool,
            :AnuncioCriadoEm
            )''',
                     item
                     )
        conn.commit()
        conn.close()

# %%

    def process_item2(self, sql):
        print('Estou no process_item_2')
        print(sql)


# %%
def main():
    parametros = Parametros(
        state='rj',
        start_url='olx.com.br',
        city='rio-de-janeiro',
        zona='zona-sul',
        transacao='venda?',
        preco_minimo='&ps=200000',
        preco_maximo='',
        ordem='sf=1',
        pagina='&o=1'
    )
    parametros.pergunta_inicial()
#   u = Urls(parametros.url_default)
    s = parametros.get_state
    su = parametros.get_start_url
    c = parametros.get_city
    z = parametros.get_zona
    t = parametros.get_transacao
    pmin = parametros.get_preco_minimo
    pmax = parametros.get_preco_maximo
    o = parametros.get_ordem
    pg = parametros.get_pagina
    ud = parametros.get_url_default
    uc = parametros.get_url_compacto
    u = Urls(s, su, c, z, t, pmin, pmax, o, pg)
    u.parse(ud, uc)


# %%
if __name__ == "__main__":
    main()
