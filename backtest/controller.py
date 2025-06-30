from datetime import datetime
from backtest.utils.binance_loader import carregar_dados_binance
from backtest.estrategias.invert_50_venda import detectar_invert50_venda
from backtest.utils.simulador import executar_simulacao

def executar_backtest_invert50(ativo='BTC/USDT', timeframe='5m', lotes=1, valor_por_ponto=1.0,
                                data_inicio=datetime(2024, 12, 1), data_fim=datetime(2024, 12, 3)):
    df = carregar_dados_binance(symbol=ativo, timeframe=timeframe, desde=data_inicio, ate=data_fim)
    sinais = detectar_invert50_venda(df)
    resultado = executar_simulacao(df, sinais)

    resultado['pnl_pontos'] = resultado.apply(
        lambda row: abs(row['preco_saida'] - row['preco_entrada']) if row['resultado'] == 'Gain'
        else -abs(row['preco_saida'] - row['preco_entrada']),
        axis=1
    )
    resultado['pnl_financeiro'] = resultado['pnl_pontos'] * lotes * valor_por_ponto
    resultado['cumulativo'] = resultado['pnl_financeiro'].cumsum()

    return resultado.round(2)
