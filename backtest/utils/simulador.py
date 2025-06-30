import pandas as pd

def executar_simulacao(df_historico, df_sinais):
    resultados = []
    if not isinstance(df_historico.index, pd.DatetimeIndex):
        df_historico.index = pd.to_datetime(df_historico.index)
    for _, sinal in df_sinais.iterrows():
        data_entrada = pd.to_datetime(sinal['data'])
        preco_entrada, stop, alvo = sinal['entrada'], sinal['stop'], sinal['alvo']
        df_futuro = df_historico[df_historico.index > data_entrada]
        resultado_trade = {"data_entrada": data_entrada, "preco_entrada": preco_entrada,
                           "stop": stop, "alvo": alvo, "resultado": "Indefinido",
                           "data_saida": None, "preco_saida": None}
        for data_candle, candle in df_futuro.iterrows():
            if candle['high'] >= stop:
                resultado_trade.update({"resultado": "Loss", "data_saida": data_candle, "preco_saida": stop})
                break
            elif candle['low'] <= alvo:
                resultado_trade.update({"resultado": "Gain", "data_saida": data_candle, "preco_saida": alvo})
                break
        resultados.append(resultado_trade)
    return pd.DataFrame(resultados)
