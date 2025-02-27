# -*- coding: utf-8 -*-
"""TCC MBA.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PXCvbDCXkf3D27o2CintxnIJb0keiAbt

#1. Importanto bibliotecas
"""

!pip install wget
import pandas as pd
import wget
from zipfile import ZipFile
!pip install numpy
import numpy as np
from google.colab.data_table import DataTable
import plotly.graph_objects as go
!pip install yfinance --upgrade --no-cache-dir
import yfinance as yf
from matplotlib import pyplot as plt

"""* Acessando a base de dados da CVM : https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/"""

url_base = 'https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/'

"""* Criando uma lista com o nome de todos os arquivos"""

arquivos_zip = []
for ano in range (2010, 2023):
  arquivos_zip.append(f'dfp_cia_aberta_{ano}.zip')
arquivos_zip

"""* Relizando o download dos arquivos da CVM e realizando a extração"""

for arq in arquivos_zip:
  wget.download(url_base+arq)

for arq in arquivos_zip:
  ZipFile(arq, 'r').extractall('CVM')

"""* Criando arquivos historicos, concatenando dados de todos anos em um unico arquivo"""

!mkdir DADOS #criando uma pasta chamada DADOS

nomes = ['BPA_con', 'BPA_ind', 'BPP_con', 'BPP_ind', 'DFC_MD_con', 'DFC_MD_ind', 'DFC_MI_con',
         'DFC_MI_ind', 'DMPL_con', 'DMPL_ind', 'DRA_con', 'DRA_ind', 'DRE_con', 'DRE_ind', 'DVA_con', 'DVA_ind']
for nome in nomes:
  arquivo = pd.DataFrame()
  for ano in range(2010, 2023):
    arquivo = pd.concat([arquivo, pd.read_csv(f'CVM/dfp_cia_aberta_{nome}_{ano}.csv', sep=';', decimal=',', encoding= 'ISO-8859-1')])
  arquivo.to_csv(f'DADOS/dfp_cia_aberta_{nome}_2010-2022.csv', index=False)

"""# 2. Preparando DRE para pegar os dados e gerar o P/L"""

dre = pd.read_csv('/content/DADOS/dfp_cia_aberta_DRE_ind_2010-2022.csv')
dre.head(5)

dre = dre[dre['ORDEM_EXERC'] == "ÚLTIMO"] # Filtrando apenas o ultimo exercicio de cada ano

dre.head(5)

"""* Filtrando por empresas

"""

empresas = dre[['DENOM_CIA','CD_CVM']].drop_duplicates().set_index('CD_CVM')
DataTable(empresas)

"""* selecionando apenas ambev"""

empresa = dre[dre['CD_CVM']== 23264]
empresa.head(5)

"""* Criando uma lista com contas da DRE"""

DataTable(empresa[['CD_CONTA', 'DS_CONTA']].drop_duplicates().set_index('CD_CONTA'))

"""* criando o P/L

  P/L = Preço por ação / Valor da açao
"""

conta = empresa[empresa['CD_CONTA']== '3.99.01.01']
conta.head()

conta.index = pd.to_datetime(conta['DT_REFER'])  #colocando a data como indice
conta.head()

"""#3. Calculando o PL"""

prices = yf.download('ABEV3.SA', start = '2010-01-01')[['Close']]

prices.head()

ambev_pl = prices.join(conta['VL_CONTA'], how='outer')

ambev_pl

ambev_pl.rename({'VL_CONTA':'LPA'}, axis=1, inplace=True)

ambev_pl.head()

ambev_pl.fillna(method='ffill',inplace=True)

ambev_pl

ambev_pl.dropna(inplace=True)
ambev_pl

ambev_pl['PL'] = ambev_pl['Close'] / ambev_pl['LPA']

DataTable(ambev_pl)

ambev_pl = ambev_pl.loc[["2012-12-31" , "2013-12-31", "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]]

ambev_pl

fig = go.Figure()
fig.add_trace(go.Scatter(x=ambev_pl.index, y=ambev_pl['PL'], name='PL'))
fig.add_trace(go.Scatter(x=ambev_pl.index, y=ambev_pl['Close'], name='ambev'))
fig.show()

"""* removendo o ano de 2013 onde o lucro foi de quase zero"""

ambev_pl_ajust = ambev_pl.loc[["2012-12-31" , "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]]

fig = go.Figure()
fig.add_trace(go.Scatter(x=ambev_pl_ajust.index, y=ambev_pl_ajust['PL'], name='PL'))
fig.add_trace(go.Scatter(x=ambev_pl_ajust.index, y=ambev_pl_ajust['Close'], name='ambev'))
fig.show()

"""# 4. Repetindo agora o processo para calculo do P/L para outras empresas"""

empresa = dre[dre['CD_CVM']== 4820]
empresa.head(5)

DataTable(empresa[['CD_CONTA', 'DS_CONTA']].drop_duplicates().set_index('CD_CONTA'))

conta = empresa[empresa['CD_CONTA']== '3.99.02.02']
conta.head()

conta.index = pd.to_datetime(conta['DT_REFER'])

prices = yf.download('BRKM5.SA', start = '2010-01-01')[['Close']]

braskem_pl = prices.join(conta['VL_CONTA'], how='outer')

braskem_pl.rename({'VL_CONTA':'LPA'}, axis=1, inplace=True)

braskem_pl

braskem_pl.fillna(method='ffill',inplace=True)
braskem_pl

DataTable(braskem_pl)

braskem_pl.dropna(inplace=True)

braskem_pl.head()

braskem_pl['PL'] = braskem_pl['Close'] / braskem_pl['LPA']

braskem_pl = braskem_pl.loc[["2012-12-31" , "2013-12-31", "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]]

braskem_pl

fig = go.Figure()
fig.add_trace(go.Scatter(x=braskem_pl.index, y=braskem_pl['PL'], name='PL'))
fig.add_trace(go.Scatter(x=braskem_pl.index, y=braskem_pl['Close'], name='BRKM5'))

"""* Agora para MGLU3	MAGAZ LUIZA =   22470

"""

empresa = dre[dre['CD_CVM']== 22470]
empresa.head(5)

DataTable(empresa[['CD_CONTA', 'DS_CONTA']].drop_duplicates().set_index('CD_CONTA'))

conta = empresa[empresa['CD_CONTA']== '3.99.01.01']
conta.head()

conta.index = pd.to_datetime(conta['DT_REFER'])

prices = yf.download('MGLU3.SA', start = '2010-01-01')[['Close']]

magalu_pl = prices.join(conta['VL_CONTA'], how='outer')

magalu_pl.rename({'VL_CONTA':'LPA'}, axis=1, inplace=True)

magalu_pl.fillna(method='ffill',inplace=True)
magalu_pl

DataTable(magalu_pl)

magalu_pl.dropna(inplace=True)

magalu_pl['PL'] = magalu_pl['Close'] / magalu_pl['LPA']

magalu_pl = magalu_pl.loc[["2012-12-31" , "2013-12-31", "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]]

magalu_pl

fig = go.Figure()
fig.add_trace(go.Scatter(x=magalu_pl.index, y=magalu_pl['PL'], name='PL'))
fig.add_trace(go.Scatter(x=magalu_pl.index, y=magalu_pl['Close'], name='MGLU3'))

"""* Calculando o P/L da PETR3	PETROBRAS =  9512"""

empresa = dre[dre['CD_CVM']== 9512]
empresa.head(5)

DataTable(empresa[['CD_CONTA', 'DS_CONTA']].drop_duplicates().set_index('CD_CONTA'))

conta = empresa[empresa['CD_CONTA']== '3.99.02.01']
conta.head()

conta.index = pd.to_datetime(conta['DT_REFER'])

prices = yf.download('PETR3.SA', start = '2010-01-01')[['Close']]

petro_pl = prices.join(conta['VL_CONTA'], how='outer')

petro_pl.rename({'VL_CONTA':'LPA'}, axis=1, inplace=True)

petro_pl.head()

petro_pl.fillna(method='ffill',inplace=True)

petro_pl.dropna(inplace=True)

petro_pl.head()

petro_pl['PL'] = petro_pl['Close'] / petro_pl['LPA']

petro_pl = petro_pl.loc[["2012-12-31" , "2013-12-31", "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]]

petro_pl

fig = go.Figure()
fig.add_trace(go.Scatter(x=petro_pl.index, y=petro_pl['PL'], name='PL'))
fig.add_trace(go.Scatter(x=petro_pl.index, y=petro_pl['Close'], name='PETR3'))

petro_pl_ajust = petro_pl.loc[["2012-12-31" , "2013-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]]

petro_pl_ajust

fig = go.Figure()
fig.add_trace(go.Scatter(x=petro_pl_ajust.index, y=petro_pl_ajust['PL'], name='PL'))
fig.add_trace(go.Scatter(x=petro_pl_ajust.index, y=petro_pl_ajust['Close'], name='PETR3'))

"""* Agora para empresa RADL3	RAIADROGASIL = 5258"""

empresa = dre[dre['CD_CVM']== 5258]
empresa.head(5)

DataTable(empresa[['CD_CONTA', 'DS_CONTA']].drop_duplicates().set_index('CD_CONTA'))

conta = empresa[empresa['CD_CONTA']== '3.99.01.01']
conta.head()

conta.index = pd.to_datetime(conta['DT_REFER'])

prices = yf.download('RADL3.SA', start = '2010-01-01')[['Close']]

raia_pl = prices.join(conta['VL_CONTA'], how='outer')

raia_pl.rename({'VL_CONTA':'LPA'}, axis=1, inplace=True)

raia_pl.fillna(method='ffill',inplace=True)
raia_pl

raia_pl.dropna(inplace=True)

raia_pl.head()

raia_pl['PL'] = raia_pl['Close'] / raia_pl['LPA']

raia_pl = raia_pl.loc[["2012-12-31" , "2013-12-31", "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]]

raia_pl

fig = go.Figure()
fig.add_trace(go.Scatter(x=raia_pl.index, y=raia_pl['PL'], name='PL'))
fig.add_trace(go.Scatter(x=raia_pl.index, y=raia_pl['Close'], name='RADL3'))

"""#5. Agora calculando o EBIT das mesmas empresas"""

ambev = dre[dre['CD_CVM']== 23264]
ambev.head()

DataTable(ambev[['CD_CONTA', 'DS_CONTA']].drop_duplicates().set_index('CD_CONTA')) # pegando codigo da conta ebit

ambev_ebit = ambev[ambev["CD_CONTA"]== "3.05"]
ambev_ebit.head(3)

ambev_ebit.index = pd.to_datetime(ambev_ebit["DT_REFER"])
ambev_ebit.head()

prices_ambev = yf.download('ABEV3.SA', start = '2010-01-01')[['Close']]

ambev_ebit = prices_ambev.join(ambev_ebit['VL_CONTA'], how = 'outer')
ambev_ebit.head()

ambev_ebit.rename({'VL_CONTA':'EBIT'}, axis=1, inplace=True)

ambev_ebit.fillna(method='ffill',inplace=True) ## preenchendo valores nulos de ebit

ambev_ebit.dropna(inplace=True)

ambev_ebit = ambev_ebit.loc[["2012-12-31" , "2013-12-31", "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]] #separando apenas os finais de ano que é quando sai o ebit, excluindo demais observações
ambev_ebit

fig = go.Figure()
fig.add_trace(go.Scatter(x=ambev_ebit.index, y=np.log10(ambev_ebit['EBIT']), name='EBIT'))
fig.add_trace(go.Scatter(x=ambev_ebit.index, y=np.log10(ambev_ebit['Close']), name='ambev'))

"""* Calculando para as demais ações"""

empresa = dre[dre['CD_CVM']== 4820]
empresa.head()

BRKM5_ebit = empresa[empresa["CD_CONTA"]== "3.05"]
BRKM5_ebit.head(3)

BRKM5_ebit.index = pd.to_datetime(BRKM5_ebit["DT_REFER"])
BRKM5_ebit.head()

prices = yf.download('BRKM5.SA', start = '2010-01-01')[['Close']]

BRKM5_ebit = prices.join(BRKM5_ebit['VL_CONTA'], how = 'outer')
BRKM5_ebit.head()

BRKM5_ebit.rename({'VL_CONTA':'EBIT'}, axis=1, inplace=True)

BRKM5_ebit.fillna(method='ffill',inplace=True) ## preenchendo valores nulos de ebit

BRKM5_ebit.dropna(inplace=True)

BRKM5_ebit = BRKM5_ebit.loc[["2012-12-31" , "2013-12-31", "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]] #separando apenas os finais de ano que é quando sai o ebit, excluindo demais observações
BRKM5_ebit

fig = go.Figure()
fig.add_trace(go.Scatter(x=BRKM5_ebit.index, y=np.log10(BRKM5_ebit['EBIT']), name='EBIT'))
fig.add_trace(go.Scatter(x=BRKM5_ebit.index, y=np.log10(BRKM5_ebit['Close']), name='braskem'))

fig = go.Figure()
fig.add_trace(go.Scatter(x=BRKM5_ebit.index, y=(BRKM5_ebit['EBIT']), name='EBIT', showlegend=True))

fig = go.Figure()
fig.add_trace(go.Scatter(x=BRKM5_ebit.index, y=(BRKM5_ebit['Close']), name='braskem', showlegend=True))

"""* Agora para empresa: MGLU3	MAGAZ LUIZA =   22470"""

empresa = dre[dre['CD_CVM']== 22470]
empresa.head()

DataTable(empresa[['CD_CONTA', 'DS_CONTA']].drop_duplicates().set_index('CD_CONTA')) # pegando codigo da conta ebit

MGLU3_ebit = empresa[empresa["CD_CONTA"]== "3.05"]
MGLU3_ebit.head(3)

MGLU3_ebit.index = pd.to_datetime(MGLU3_ebit["DT_REFER"])
MGLU3_ebit.head()

prices = yf.download('MGLU3.SA', start = '2010-01-01')[['Close']]

MGLU3_ebit = prices.join(MGLU3_ebit['VL_CONTA'], how = 'outer')
MGLU3_ebit.head()

MGLU3_ebit.rename({'VL_CONTA':'EBIT'}, axis=1, inplace=True)

MGLU3_ebit.fillna(method='ffill',inplace=True) ## preenchendo valores nulos de ebit

MGLU3_ebit.dropna(inplace=True)

MGLU3_ebit = MGLU3_ebit.loc[["2012-12-31" , "2013-12-31", "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]] #separando apenas os finais de ano que é quando sai o ebit, excluindo demais observações
MGLU3_ebit

fig = go.Figure()
fig.add_trace(go.Scatter(x=MGLU3_ebit.index, y=np.log10(MGLU3_ebit['EBIT']), name='EBIT'))
fig.add_trace(go.Scatter(x=MGLU3_ebit.index, y=np.log10(MGLU3_ebit['Close']), name='magalu'))

"""* Agora para empresa: PETR3	PETROBRAS =  9512"""

empresa = dre[dre['CD_CVM']== 9512]
empresa.head()

DataTable(empresa[['CD_CONTA', 'DS_CONTA']].drop_duplicates().set_index('CD_CONTA')) # pegando codigo da conta ebit

PETR3_ebit = empresa[empresa["CD_CONTA"]== "3.05"]
PETR3_ebit.head(3)

PETR3_ebit.index = pd.to_datetime(PETR3_ebit["DT_REFER"])
PETR3_ebit.head()

prices = yf.download('PETR3.SA', start = '2010-01-01')[['Close']]

DataTable(prices)

PETR3_ebit = prices.join(PETR3_ebit['VL_CONTA'], how = 'outer')
PETR3_ebit.head()

PETR3_ebit.rename({'VL_CONTA':'EBIT'}, axis=1, inplace=True)

PETR3_ebit.fillna(method='ffill',inplace=True) ## preenchendo valores nulos de ebit

PETR3_ebit.dropna(inplace=True)

DataTable(PETR3_ebit)

PETR3_ebit = PETR3_ebit.loc[["2012-12-31" , "2013-12-31", "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]] #separando apenas os finais de ano que é quando sai o ebit, excluindo demais observações
PETR3_ebit

fig = go.Figure()
fig.add_trace(go.Scatter(x=PETR3_ebit.index, y=np.log10(PETR3_ebit['EBIT']), name='EBIT'))
fig.add_trace(go.Scatter(x=PETR3_ebit.index, y=np.log10(PETR3_ebit['Close']), name='petro'))

fig = go.Figure()
fig.add_trace(go.Scatter(x=PETR3_ebit.index, y=(PETR3_ebit['EBIT']), name='EBIT', showlegend=True))

fig = go.Figure()
fig.add_trace(go.Scatter(x=PETR3_ebit.index, y=PETR3_ebit['Close'], name='petro', showlegend=True))

"""* E por final para a empresa: RADL3	RAIADROGASIL = 5258"""

empresa = dre[dre['CD_CVM']== 5258]
empresa.head()

DataTable(empresa[['CD_CONTA', 'DS_CONTA']].drop_duplicates().set_index('CD_CONTA')) # pegando codigo da conta ebit

RADL3_ebit = empresa[empresa["CD_CONTA"]== "3.05"]
RADL3_ebit.head(3)

RADL3_ebit.index = pd.to_datetime(RADL3_ebit["DT_REFER"])
RADL3_ebit.head()

prices = yf.download('RADL3.SA', start = '2010-01-01')[['Close']]

DataTable(prices)

RADL3_ebit = prices.join(RADL3_ebit['VL_CONTA'], how = 'outer')
RADL3_ebit.head()

RADL3_ebit.rename({'VL_CONTA':'EBIT'}, axis=1, inplace=True)

RADL3_ebit.fillna(method='ffill',inplace=True) ## preenchendo valores nulos de ebit

RADL3_ebit.dropna(inplace=True)

RADL3_ebit = RADL3_ebit.loc[["2012-12-31" , "2013-12-31", "2014-12-31", "2015-12-31",
                "2016-12-31", "2017-12-31", "2018-12-31", "2019-12-31",
                "2020-12-31", "2021-12-31", "2022-12-31"]] #separando apenas os finais de ano que é quando sai o ebit, excluindo demais observações
RADL3_ebit

fig = go.Figure()
fig.add_trace(go.Scatter(x=RADL3_ebit.index, y=np.log10(RADL3_ebit['EBIT']), name='EBIT'))
fig.add_trace(go.Scatter(x=RADL3_ebit.index, y=np.log10(RADL3_ebit['Close']), name='RADL3'))

"""* criando uma visualização com todo os dados de uma vez"""

fig = go.Figure()
fig.add_trace(go.Scatter(x=ambev_ebit.index, y=np.log10(ambev_ebit['EBIT']), name='EBIT-AMBEV'))
fig.add_trace(go.Scatter(x=ambev_ebit.index, y=np.log10(ambev_ebit['Close']), name='ambev'))
fig.add_trace(go.Scatter(x=BRKM5_ebit.index, y=np.log10(BRKM5_ebit['EBIT']), name='EBIT-BRASKEM'))
fig.add_trace(go.Scatter(x=BRKM5_ebit.index, y=np.log10(BRKM5_ebit['Close']), name='braskem'))
fig.add_trace(go.Scatter(x=MGLU3_ebit.index, y=np.log10(MGLU3_ebit['EBIT']), name='EBIT-MAGALU'))
fig.add_trace(go.Scatter(x=MGLU3_ebit.index, y=np.log10(MGLU3_ebit['Close']), name='magalu'))
fig.add_trace(go.Scatter(x=PETR3_ebit.index, y=np.log10(PETR3_ebit['EBIT']), name='EBIT-PETRO'))
fig.add_trace(go.Scatter(x=PETR3_ebit.index, y=np.log10(PETR3_ebit['Close']), name='petro'))
fig.add_trace(go.Scatter(x=RADL3_ebit.index, y=np.log10(RADL3_ebit['EBIT']), name='EBIT-RAIA'))
fig.add_trace(go.Scatter(x=RADL3_ebit.index, y=np.log10(RADL3_ebit['Close']), name='RAIA'))

fig = go.Figure()
fig.add_trace(go.Scatter(x=ambev_pl_ajust.index, y=ambev_pl_ajust['PL'], name='PL-ambev'))
fig.add_trace(go.Scatter(x=ambev_pl_ajust.index, y=ambev_pl_ajust['Close'], name='ambev'))
fig.add_trace(go.Scatter(x=braskem_pl.index, y=braskem_pl['PL'], name='PL-braskem'))
fig.add_trace(go.Scatter(x=braskem_pl.index, y=braskem_pl['Close'], name='BRKM5'))
fig.add_trace(go.Scatter(x=magalu_pl.index, y=magalu_pl['PL'], name='PL-magalu'))
fig.add_trace(go.Scatter(x=magalu_pl.index, y=magalu_pl['Close'], name='MGLU3'))
fig.add_trace(go.Scatter(x=petro_pl_ajust.index, y=petro_pl_ajust['PL'], name='PL-petro'))
fig.add_trace(go.Scatter(x=petro_pl_ajust.index, y=petro_pl_ajust['Close'], name='PETR3'))
fig.add_trace(go.Scatter(x=raia_pl.index, y=raia_pl['PL'], name='PL-raia'))
fig.add_trace(go.Scatter(x=raia_pl.index, y=raia_pl['Close'], name='RADL3'))
fig.show()