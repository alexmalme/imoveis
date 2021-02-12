import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 
import numpy as np 
import scipy.stats
import os
import re
import time
#%matplotlib inline

time_today = time.strftime("%Y_%m_%d_%H_%M")
timestamp = time.strftime("%Y%m%d%H%M")

# escreva o caminho do arquivo
#file = ''
#file_invs = '
zone = re.compile(r'(zona[-|_][a-z]*)').search(file).group(0)
arquivo = re.compile(r'(zona[-|_][a-z].*[^_.csv])').search(file).group(0)
path = '/home/alx/dataestate/'

plt.style.use('seaborn-whitegrid')
sns.set_style("white")
large = 22; med = 16; small = 12
params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (20, 15),
          'axes.labelsize': med,
          'axes.titlesize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)




numerical = {
                    'AnuncioBanheiros',
                    'AnuncioQuartos',
                    'AnuncioSuites',
                    'AnuncioDiasDesdeCriacaoCod',
                    'AnuncioVagasGaragem',
                    'AreaTotal',
                    'AreaUtil',
                    'PrecoVenda',
                    'PrecoM2',
                    'Preco Imoveis Similares',
                    'Preco m2 Imóveis Similares',
                    'PrecoAluguel',
                    'MediaM2',
                    'MediaPreco',
                    'MedianaBairroAreaTotal',
                    'MedianaM2Relacoes',
                    'MedianaPrecoM2Rua',
                    'MedianaPrecoRelacoes', 
                    'Porcentagem'
}

categorical = {
                        'Bairro',
                        '% PrecoVenda/valor de mercado',
                        'AnuncioEnderecoRua',
                        'AnuncioEnderecoCep',
                        'AnuncioAnuncianteContatoTelefone',
                        'ContaNome',
                        'ContaEmailPrincipal',
                        'ContaSiteURL',
                        'PrecoReais',
                        'TipoAnunciante',
                        'Possui Vaga'
}



df_ = pd.read_csv(file, sep=',',  low_memory=False)


data = df_.loc[(df_['AnuncioQuartos'] < 6) & (df_['AnuncioBanheiros'] < 10) & (df_['AnuncioVagasGaragem'] < 10) & (df_['AreaTotal'] < 1000) & (df_['TipoImovel'] != 'terreno') & (df_['AreaTotal'] < 1000) & (df_['PrecoVenda'] < 10000000) & (df_['PrecoVenda'] > 150000) & (df_['PrecoM2'] < 40000),:]


data_5m = data.loc[(data['PrecoVenda'] < 5_000_000) & (data['PrecoM2'] < 25_000),: ]
data_5m.loc[:,'PrecoVendaPlot'] = data_5m.loc[:,'PrecoVenda'] / 1000
data_5m.loc[:,'PrecoM2Plot'] =data_5m['PrecoM2']  / 1000


data_5m_vaga = data_5m.loc[data_5m['VagasBool'] == True,:]
data_5m_sem_vaga = data_5m.loc[data_5m['VagasBool'] == False,:]



def PrecoVenda_imoveis_bairro():
    df_menor = data_5m.loc[(data_5m['Bairro'] == 'Botafogo') | (data_5m['Bairro'] == 'Catete') | (data_5m['Bairro'] == 'Cosme Velho') | (data_5m['Bairro'] == 'Flamengo') | (data_5m['Bairro'] == 'Glória') | (data_5m['Bairro'] == 'Humaitá') | (data_5m['Bairro'] == 'Laranjeiras') | (data_5m['Bairro'] == 'Urca'), :]
    
    plt.figure(figsize=(20,15))
    g = sns.catplot(x='Bairro', y='PrecoVendaPlot', kind='boxen', data=df_menor.sort_values('Bairro'), height=8.27, aspect=15/8.27)
    g.despine(offset=10, trim=True)
    g.set_axis_labels('Bairros', 'Valores em R$1.000')
    plt.title('Preços Imóveis Bairros - Geral')
    plt.xticks(rotation=-60)
    plt.show(g)
    path_ = path + 'preco_imoveis_bairro_geral_'
    g.savefig(f'{path_}{arquivo}{zone}_menor.png', dpi=200)
    plt.close()


    df_maior = data_5m.loc[(data_5m['Bairro'] == 'Arpoador') | (data_5m['Bairro'] == 'Copacabana') | (data_5m['Bairro'] == 'Gávea') | (data_5m['Bairro'] == 'Ipanema') | (data_5m['Bairro'] == 'Jardim Botânico') | (data_5m['Bairro'] == 'Lagoa') | (data_5m['Bairro'] == 'Leblon') | (data_5m['Bairro'] == 'Leme') | (data_5m['Bairro'] == 'São Conrado'), :]
    
    plt.figure(figsize=(20,15))
    g = sns.catplot(x='Bairro', y='PrecoVendaPlot', kind='boxen', data=df_maior.sort_values('Bairro'), height=8.27, aspect=15/8.27)
    g.despine(offset=10, trim=True)
    g.set_axis_labels('Bairros', 'Valores em R$1.000')
    plt.title('Preços Imóveis Bairros - Geral')
    plt.xticks(rotation=-60)
    plt.show(g)
    path_ = path + 'preco_imoveis_bairro_geral_'
    g.savefig(f'{path_}{arquivo}{zone}_maior.png', dpi=200)
    plt.close()



def m2_imoveis_bairro_geral():
    df_menor = data_5m.loc[(data_5m['Bairro'] == 'Botafogo') | (data_5m['Bairro'] == 'Catete') | (data_5m['Bairro'] == 'Cosme Velho') | (data_5m['Bairro'] == 'Flamengo') | (data_5m['Bairro'] == 'Glória') | (data_5m['Bairro'] == 'Humaitá') | (data_5m['Bairro'] == 'Laranjeiras') | (data_5m['Bairro'] == 'Urca'), :]

    plt.figure(figsize=(20,15))
    g = sns.catplot(x='Bairro', y='PrecoM2Plot', kind='boxen', data=df_menor.sort_values('Bairro'), height=8.27, aspect=15/8.27)
    g.despine(offset=10, trim=True)
    g.set_axis_labels('Bairros', 'Valores em R$1.000')
    plt.title('Preços Médios M2 por Bairro - Geral')
    plt.xticks(rotation=-60)
    plt.show(g)
    path_ = path + 'm2_imoveis_bairro_geral_'
    g.savefig(f'{path_}{arquivo}{zone}_menor.png', dpi=200)
    plt.close()


    df_maior = data_5m.loc[(data_5m['Bairro'] == 'Arpoador') | (data_5m['Bairro'] == 'Copacabana') | (data_5m['Bairro'] == 'Gávea') | (data_5m['Bairro'] == 'Ipanema') | (data_5m['Bairro'] == 'Jardim Botânico') | (data_5m['Bairro'] == 'Lagoa') | (data_5m['Bairro'] == 'Leblon') | (data_5m['Bairro'] == 'Leme') | (data_5m['Bairro'] == 'São Conrado'), :]

       
    plt.figure(figsize=(20,15))
    g = sns.catplot(x='Bairro', y='PrecoM2Plot', kind='boxen', data=df_maior.sort_values('Bairro'), height=8.27, aspect=15/8.27)
    g.despine(offset=10, trim=True)
    g.set_axis_labels('Bairros', 'Valores em R$1.000')
    plt.title('Preços Médios M² por Bairro - Geral')
    plt.xticks(rotation=-60)
    plt.show(g)
    path_ = path + 'm2_imoveis_bairro_geral_'
    g.savefig(f'{path_}{arquivo}{zone}_maior.png', dpi=200)
    plt.close()







def m2_imoveis_bairro_vaga():
    df_menor = data_5m_vaga.loc[(data_5m_vaga['Bairro'] == 'Botafogo') | (data_5m_vaga['Bairro'] == 'Catete') | (data_5m_vaga['Bairro'] == 'Cosme Velho') | (data_5m_vaga['Bairro'] == 'Flamengo') | (data_5m_vaga['Bairro'] == 'Glória') | (data_5m_vaga['Bairro'] == 'Humaitá') | (data_5m_vaga['Bairro'] == 'Laranjeiras') | (data_5m_vaga['Bairro'] == 'Urca'), :]

    plt.figure(figsize=(20,15))
    g = sns.catplot(x='Bairro', y='PrecoM2Plot', kind='boxen', data=df_menor.sort_values('Bairro'), height=8.27, aspect=15/8.27)
    g.despine(offset=10, trim=True)
    g.set_axis_labels('Bairros', 'Valores em R$1.000')
    plt.title('Preços Médios M² por Bairro - Com Vaga')
    plt.xticks(rotation=-60)
    plt.show(g)
    path_ = path + 'm2_imoveis_bairro_com_vaga_'
    g.savefig(f'{path_}{arquivo}{zone}_menor.png', dpi=200)
    plt.close()



    df_maior = data_5m_vaga.loc[(data_5m_vaga['Bairro'] == 'Arpoador') | (data_5m_vaga['Bairro'] == 'Copacabana') | (data_5m_vaga['Bairro'] == 'Gávea') | (data_5m_vaga['Bairro'] == 'Ipanema') | (data_5m_vaga['Bairro'] == 'Jardim Botânico') | (data_5m_vaga['Bairro'] == 'Lagoa') | (data_5m_vaga['Bairro'] == 'Leblon') | (data_5m_vaga['Bairro'] == 'Leme') | (data_5m_vaga['Bairro'] == 'São Conrado'), :]

    plt.figure(figsize=(20,15))
    g = sns.catplot(x='Bairro', y='PrecoM2Plot', kind='boxen', data=df_maior.sort_values('Bairro'), height=8.27, aspect=15/8.27)
    g.despine(offset=10, trim=True)
    g.set_axis_labels('Bairros', 'Valores em R$1.000')
    plt.title('Preços Médios M² por Bairro - Com Vaga')
    plt.xticks(rotation=-60)
    plt.show(g)
    path_ = path + 'm2_imoveis_bairro_com_vaga_'
    g.savefig(f'{path_}{arquivo}{zone}_maior.png', dpi=200)
    plt.close()





def m2_imoveis_bairro_sem_vaga():
    df_menor = data_5m_sem_vaga.loc[(data_5m_sem_vaga['Bairro'] == 'Botafogo') | (data_5m_sem_vaga['Bairro'] == 'Catete') | (data_5m_sem_vaga['Bairro'] == 'Cosme Velho') | (data_5m_sem_vaga['Bairro'] == 'Flamengo') | (data_5m_sem_vaga['Bairro'] == 'Glória') | (data_5m_sem_vaga['Bairro'] == 'Humaitá') | (data_5m_sem_vaga['Bairro'] == 'Laranjeiras') | (data_5m_sem_vaga['Bairro'] == 'Urca'), :]
    
    plt.figure(figsize=(20,15))
    g = sns.catplot(x='Bairro', y='PrecoM2Plot', kind='boxen', data=df_menor.sort_values('Bairro'), height=8.27, aspect=15/8.27)
    g.despine(offset=10, trim=True)
    g.set_axis_labels('Bairros', 'Valores em R$1.000')
    plt.title('Preços Médios M² por Bairros - Sem Vaga')
    plt.xticks(rotation=-60)
    plt.show(g)
    path_ = path + 'm2_imoveis_bairro_sem_vaga_'
    g.savefig(f'{path_}{zone}_menor.png', dpi=200)
    plt.close()

    df_maior = data_5m_sem_vaga.loc[(data_5m_sem_vaga['Bairro'] == 'Arpoador') | (data_5m_sem_vaga['Bairro'] == 'Copacabana') | (data_5m_sem_vaga['Bairro'] == 'Gávea') | (data_5m_sem_vaga['Bairro'] == 'Ipanema') | (data_5m_sem_vaga['Bairro'] == 'Jardim Botânico') | (data_5m_sem_vaga['Bairro'] == 'Lagoa') | (data_5m_sem_vaga['Bairro'] == 'Leblon') | (data_5m_sem_vaga['Bairro'] == 'Leme') | (data_5m_sem_vaga['Bairro'] == 'São Conrado'), :]

    plt.figure(figsize=(20,15))
    g = sns.catplot(x='Bairro', y='PrecoM2Plot', kind='boxen', data=df_maior.sort_values('Bairro'), height=8.27, aspect=15/8.27)
    g.despine(offset=10, trim=True)
    g.set_axis_labels('Bairros', 'Valores em R$1.000')
    plt.title('Preços Médios M² por Bairros - Sem Vaga')
    plt.xticks(rotation=-60)
    plt.show(g)
    path_ = path + 'm2_imoveis_bairro_sem_vaga_'
    g.savefig(f'{path_}{arquivo}{zone}_maior.png', dpi=200)
    plt.close()



def imoveis_bairro():
    plt.figure(figsize=(20,15))
    g = sns.countplot(y='Bairro', data=data.sort_values('Bairro'), order=sorted([*set(data['Bairro'])]))
    plt.xticks(rotation=-45)
    g.set_xlabel('Total Imóveis')
    g.set_ylabel('')
    plt.title('Quantidade Imóveis por Bairros')
    plt.tight_layout()
    plt.show(g)
    figure = g.get_figure()
    path_ = path + 'imoveis_bairro_'
    figure.savefig(f'{path}{arquivo}{zone}_quantidade_imoveis.png', dpi=200)
    plt.close()




def quantidade_quartos(df):
    df_ = df.copy()
    lista_bairros = [*set(df_['Bairro'])]
    #ruas caras
    for b in lista_bairros:
        labels = ['Com Vaga', 'Sem Vaga']
        df_['VagasBool'] = df_.VagasBool.replace({0:'Sem Vaga', 1: 'Com Vaga'})
        data = df_[df_['Bairro'] == b]
        num = data['Bairro'].count()
        g = sns.countplot(x=data['AnuncioQuartos'].astype('int64'),   hue="VagasBool", data=data, palette={'Com Vaga': 'C0', 'Sem Vaga': 'C1'}, hue_order=labels)
        g.set(ylabel=f'Nº Imóveis')
        plt.title(f'{b} - Total Imóveis: {num}')
        h, l = g.get_legend_handles_labels()
        g.legend(h, labels, title="Vagas")
        plt.tight_layout()
        plt.show(g)
        path_ = path + 'quantidade_quartos_'
        figure = g.get_figure()
        figure.savefig(f'{path_}{arquivo}{b}_quantidade_quartos.png', dpi=200)
        plt.close()



def mais_caros(df):
    df_ = df.copy()
    df_['PrecoVendaPlot'] = df_.loc[:,'PrecoVenda'] / 1000
    lista_bairros = [*set(df_['Bairro'])]
    #ruas caras
    for b in lista_bairros:
        lista_caros = df_[df_['Bairro'] == b].groupby('AnuncioEnderecoRua')['PrecoM2'].mean().astype('int64').divide(1000,  fill_value = 0.0).nlargest(20)
        sns.set(style="whitegrid")
        plt.figure(figsize=(20,15))
        g = sns.stripplot(y=lista_caros.index, x=[*lista_caros], size=15, color='b')
        plt.xticks(rotation=-45)
        g.set(xlabel='Preço M² em R$1.000', ylabel='Ruas')
        plt.title(f'20 Ruas M² Mais Valorizado {b}', fontsize=22)
        plt.tight_layout()
        plt.show(g)
        figure = g.get_figure()
        path_ = path + 'ruas_m2_mais_valorizado_'
        figure.savefig(f'{path_}{arquivo}{b}.png', dpi=200)
        plt.close()

  



def distribuicao():
    sns.set(style='whitegrid', palette="deep", font_scale=1.1, rc={"figure.figsize": [8, 5]})
    sns.distplot(
    df_['PrecoVenda']/1000, norm_hist=False, bins=20,kde=False, hist_kws={"alpha": 1}
    ).set(xlabel='Preço de Venda em 1.000', ylabel='Nº Imóveis em 1.000', title='Distribuiçao Imóveis')





def investimentos(df):
    df_inv = data[data['ValidaInvestimento'] == True]
    df_inv = df_inv.rename(columns= {'MediaAgrupadaValidaInvestimentoPrecoVenda':
                                                    'Preco Imoveis Similares', 
                                                    'MediaAgrupadaValidaInvestimentoM2':
                                                    'Preco m2 Imoveis Similares',
                                                    'VagasBool': 'TemVaga',
                                                    'PorcentagemTexto': f'% preco/valor de mercado'
                                                    })
    PrecoVendas = [*zip(df_inv['Preco Imoveis Similares'], df_inv['PrecoVenda'], \
                df_inv['Preco m2 Imoveis Similares'], df_inv['PrecoM2'], df_inv['% preco/valor de mercado'], list(df_inv.index), df_inv['AnuncioEnderecoRua'], df_inv['AnuncioEnderecoBairro'])]

    large = 22; med = 16; small = 12
    params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (15, 10),
          'axes.labelsize': med,
          'axes.titlesize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
    plt.rcParams.update(params)
    for i in range(len(PrecoVendas)):
        labels = ['']
        PrecoVenda_m = PrecoVendas[i][0]/1000
        PrecoVenda_i = PrecoVendas[i][1]/1000
        diff = (PrecoVendas[i][0]/1000) - (PrecoVendas[0][1]/1000)
        perc = PrecoVendas[i][4]
        idx = PrecoVendas[i][5]
        bairro = PrecoVendas[i][6]
        rua = PrecoVendas[i][7]
        PrecoVenda_m_label = str(int(PrecoVendas[i][0]))
        PrecoVenda_i_label = str(int(PrecoVendas[i][1]))
        if len(str(PrecoVenda_m_label)) < 7:
            pmlabel = str(PrecoVenda_m_label)[:-3] + '.' + str(PrecoVenda_m_label)[-3:]
        elif len(str(PrecoVenda_m_label)) >= 7:
            pmlabel = str(PrecoVenda_m_label)[:-6]+ '.' + str(PrecoVenda_m_label)[-6:-3] + '.' + str(PrecoVenda_m_label)[-3:]
        if len(str(PrecoVenda_i_label)) < 7:
            pilabel = str(PrecoVenda_i_label)[:-3] + '.' + str(PrecoVenda_i_label)[-3:]
        elif len(str(PrecoVenda_i_label)) >= 7:
            pilabel = str(PrecoVenda_i_label)[:-6]+ '.' + str(PrecoVenda_i_label)[-6:-3] + '.' + str(PrecoVenda_i_label)[-3:]
            
        x = np.arange(len(labels))  # the label locations
        width = 0.25  # the width of the bars


        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width/4, PrecoVenda_m, width*.35, label=f'Preço de Mercado R$ {pmlabel}', color= '#0080ff')
        rects2 = ax.bar(x + width/4, PrecoVenda_i, width*.35, label=f'Preço Oportunidade R$ {pilabel}\nRetorno {perc}', color='#ffbf00')
        #p2 = plt.bar(x + width, PrecoVenda_m - PrecoVenda_i, width, label= f'Retorno Percentual {perc}',bottom=PrecoVenda_i, color='#2dd22d')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Valores em 1e3')
        ax.set_title(f'Demonstrativo Retornos {rua} {bairro} - COD: {idx}')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        fig.tight_layout()
        plt.show()
        path_ = path + 'investimentos_'
        fig.savefig(f'{path_}{arquivo}{bairro}_{rua}_{idx}.png', dpi=100)
        plt.close()
        


def correlacao(df):
    df_ = df.copy()
    lista_bairros = [*set(df_['Bairro'])]
    columns_ = ['Bairro','PrecoVenda',  'AreaUtil', 'AreaTotal',  'AnuncioQuartos', 'AnuncioSuites', 'AnuncioBanheiros', 'AnuncioVagasGaragem']
    df_ = df_[columns_].rename({'PrecoVenda': 'Preço',  'AreaUtil': 'Area Util', 'AreaTotal': 'Area Total',  'AnuncioQuartos': 'Quartos', 'AnuncioSuites': 'Suítes', 'AnuncioBanheiros': 'Banheiros', 'AnuncioVagasGaragem': 'Vagas'}, axis='columns')
    for b in lista_bairros:
        corr = df_.loc[df_['Bairro'] == b, :].corr()
        num = df_['Bairro'].count()
        plt.figure(figsize=(15,15))
        plt.rcParams['font.size'] = 16
        g = sns.heatmap(corr, cmap='coolwarm', square=True, robust=True)
        plt.title(f'{b} - Mapa de Calor/Correlação', fontsize=18)
        path_ = path + 'correlacao_'
        plt.show(g)
        figure = g.get_figure()
        figure.tight_layout()
        figure.savefig(f'{path_}{arquivo}{b}_correlacao.png', dpi=200)
        plt.close()
    

def corr_plot(df, bairro):
    plt.figure(figsize=(10,10))
    x = [*df['ContaEmailPrincipal'].value_counts().iloc[:10]]
    labels = [*df['ContaEmailPrincipal'].value_counts().iloc[0:10].index]
    g = sns.barplot(y=labels, x=x, palette='Greens_d')
    plt.title(f'Mais Anúncios {bairro}')
    g.set(ylabel ='', xlabel ='Quantidade Imóveis Anunciados') 
    plt.tight_layout()
    plt.show(g)
    figure = g.get_figure()
    path_ = path + 'corretores_anuncios_'
    figure.savefig(f'{path}{arquivo}{bairro}_quantidade.png', dpi=100)
    plt.close()


def corretores(df):
    df_ = df.copy()
    df_ = df_[df_['TipoAnunciante'] == 'profissional'].drop_duplicates('LinkHref').reindex()
    lista_bairros = [*set(df_['Bairro'])]
    dfs = [df_[df_['Bairro'] == b] for b in lista_bairros]
    for frame in dfs:
        series_ = [*frame['Bairro']]
        bairro = series_[0]
        plota = corr_plot(frame, bairro)

    




def main():
    PrecoVenda_imoveis_bairro()
    m2_imoveis_bairro_geral()
    m2_imoveis_bairro_vaga()
    m2_imoveis_bairro_sem_vaga()
    imoveis_bairro()
    mais_caros(df_) 
    investimentos(df_)
    quantidade_quartos(df_)
    correlacao(df_)
    corretores(df_)



if  __name__ == "__main__":
    main()
