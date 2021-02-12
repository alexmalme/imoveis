import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns

# Escrever o caminho dos arquivos
#p = Path('/home/alx_malme/imoveis')
#imoveis = 'tudo_2020_10_22_20_36.xlsx'

file = f'{p.as_posix()}/{imoveis}'
df = pd.read_excel(file)
df_ = df.copy()
colunas = [*df.columns]
colunas_num = [
    'AnuncioBanheiros',
    'AnuncioEnderecoCep',
    'AnuncioEnderecoLatitude',
    'AnuncioEnderecoLongitude',
    'AnuncioQuartos',
    'AnuncioSuites',
    'AnuncioVagasGaragem',
    'AreaTotal',
    'AreaUtil',
    'PrecoM2',
    'PrecoVenda',
]
df.loc[df['AnuncioSuites'].isna(), 'AnuncioSuites'] = 0
df.loc[df['AnuncioVagasGaragem'].isna(), 'AnuncioVagasGaragem'] = 0
d = df[colunas_num]
d = d.dropna()
X = d.drop("PrecoVenda", axis=1).select_dtypes(include=np.number).values
y = d['PrecoVenda'].values.reshape(-1, 1)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)
reg_all = LinearRegression()
reg_all.fit(X_train, y_train)
y_pred_reg = reg_all.predict(X_test)
print(reg_all.score(X_test, y_test))
ridge = Ridge(alpha=0.2, normalize=True).fit(X_train, y_train)
y_pred_ridge = ridge.predict(X_test)
print(ridge.score(X_test, y_test))
lasso = Lasso(alpha=0.2, normalize=True).fit(X_train, y_train)
y_pred_lasso = lasso.predict(X_test)
print(lasso.score(X_test, y_test))
