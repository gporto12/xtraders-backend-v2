import pandas as pd
import numpy as np

def detectar_invert50_venda(df, mme_curta=9, mme_media=20, mme_longa=50, mme_geral=200, tolerancia_alinhamento=3, tolerancia_toque=2):
    df_copy = df.copy()
    df_copy[f'MME{mme_curta}'] = df_copy['close'].ewm(span=mme_curta, adjust=False).mean()
    df_copy[f'MME{mme_media}'] = df_copy['close'].ewm(span=mme_media, adjust=False).mean()
    df_copy[f'MME{mme_longa}'] = df_copy['close'].ewm(span=mme_longa, adjust=False).mean()
    df_copy[f'MME{mme_geral}'] = df_copy['close'].ewm(span=mme_geral, adjust=False).mean()
    df_copy['alinhadas'] = ((df_copy[f'MME{mme_longa}'] > df_copy[f'MME{mme_media}']) &
                            (df_copy[f'MME{mme_media}'] > df_copy[f'MME{mme_curta}']) &
                            ((df_copy[f'MME{mme_longa}'] - df_copy[f'MME{mme_media}']) > tolerancia_alinhamento) &
                            ((df_copy[f'MME{mme_media}'] - df_copy[f'MME{mme_curta}']) > tolerancia_alinhamento))
    df_copy['tocou_longa'] = abs(df_copy['low'] - df_copy[f'MME{mme_longa}']) <= tolerancia_toque
    df_copy['candle_forte'] = ((df_copy['close'].shift(-1) < df_copy[f'MME{mme_media}'].shift(-1)) &
                               (df_copy['close'].shift(-1) < df_copy['open'].shift(-1)))
    df_copy['sinal_valido'] = df_copy['alinhadas'] & df_copy['tocou_longa'] & df_copy['candle_forte']
    sinais_df = df_copy[df_copy['sinal_valido']].copy()
    if sinais_df.empty:
        return pd.DataFrame(columns=['data', 'entrada', 'stop', 'alvo'])
    sinais_df['entrada'] = df_copy.loc[sinais_df.index, 'close'].shift(-1)
    sinais_df['stop'] = np.maximum(df_copy.loc[sinais_df.index, 'high'], df_copy['high'].shift(-1))
    mme_geral_entrada = df_copy.loc[sinais_df.index, f'MME{mme_geral}'].shift(-1)
    mme_geral_visivel = mme_geral_entrada > sinais_df['entrada']
    sinais_df['alvo'] = np.where(mme_geral_visivel,
                                 mme_geral_entrada,
                                 sinais_df['entrada'] - 2 * (sinais_df['stop'] - sinais_df['entrada']))
    resultado = sinais_df[['entrada', 'stop', 'alvo']].dropna().copy()
    resultado.reset_index(inplace=True)
    nome_coluna_data = resultado.columns[0]
    resultado['data'] = resultado[nome_coluna_data].dt.strftime('%Y-%m-%d %H:%M:%S')
    resultado = resultado[['data', 'entrada', 'stop', 'alvo']].round(2)
    return resultado
