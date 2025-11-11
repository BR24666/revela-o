"""
Módulo de coleta de dados da Binance
"""
import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta
import time
from typing import Optional, List
from config import SYMBOL, TIMEFRAME, BINANCE_API_KEY, BINANCE_API_SECRET

class BinanceDataCollector:
    def __init__(self):
        """
        Inicializa o coletor de dados da Binance.
        Não requer API key/secret para dados públicos.
        """
        if BINANCE_API_KEY and BINANCE_API_SECRET:
            self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        else:
            self.client = Client()
    
    def get_historical_klines(
        self, 
        symbol: str = SYMBOL,
        interval: str = TIMEFRAME,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Coleta dados históricos de candles (OHLCV).
        
        Args:
            symbol: Par de trading (ex: 'BTCUSDT')
            interval: Timeframe (ex: '1m', '5m', '1h')
            start_date: Data inicial (formato: 'YYYY-MM-DD')
            end_date: Data final (formato: 'YYYY-MM-DD')
            limit: Número máximo de velas (max 1000 por request)
            
        Returns:
            DataFrame com colunas: timestamp, open, high, low, close, volume
        """
        try:
            if start_date:
                start_date = start_date
            else:
                # Por padrão, coleta os últimos 1000 candles
                start_date = None
            
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_date,
                end_str=end_date,
                limit=limit
            )
            
            # Converter para DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Processar dados
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            # Selecionar apenas colunas relevantes
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except Exception as e:
            print(f"Erro ao coletar dados históricos: {e}")
            return pd.DataFrame()
    
    def get_large_historical_dataset(
        self,
        symbol: str = SYMBOL,
        interval: str = TIMEFRAME,
        years: int = 3
    ) -> pd.DataFrame:
        """
        Coleta um grande conjunto de dados históricos (para treinamento).
        A API da Binance limita 1000 velas por request, então fazemos múltiplas chamadas.
        
        Args:
            symbol: Par de trading
            interval: Timeframe
            years: Quantos anos de dados coletar
            
        Returns:
            DataFrame com todos os dados históricos
        """
        print(f"Coletando {years} anos de dados históricos para {symbol}...")
        
        all_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        current_start = start_date
        
        while current_start < end_date:
            # Calcular end para este batch (1000 velas de 1min = ~16.6 horas)
            if interval == '1m':
                current_end = current_start + timedelta(hours=16)
            elif interval == '5m':
                current_end = current_start + timedelta(hours=83)
            else:
                current_end = current_start + timedelta(days=30)
            
            if current_end > end_date:
                current_end = end_date
            
            # Coletar batch
            batch_df = self.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_date=current_start.strftime('%Y-%m-%d'),
                end_date=current_end.strftime('%Y-%m-%d'),
                limit=1000
            )
            
            if not batch_df.empty:
                all_data.append(batch_df)
                print(f"Coletado batch: {current_start.strftime('%Y-%m-%d')} até {current_end.strftime('%Y-%m-%d')}")
            
            # Próximo batch
            current_start = current_end
            
            # Evitar rate limiting
            time.sleep(0.5)
        
        # Concatenar todos os batches
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            final_df = final_df.drop_duplicates(subset=['timestamp'])
            final_df = final_df.sort_values('timestamp').reset_index(drop=True)
            
            print(f"✓ Total de velas coletadas: {len(final_df)}")
            print(f"✓ Período: {final_df['timestamp'].min()} até {final_df['timestamp'].max()}")
            
            return final_df
        else:
            print("Erro: Nenhum dado foi coletado")
            return pd.DataFrame()
    
    def get_latest_candles(self, symbol: str = SYMBOL, interval: str = TIMEFRAME, limit: int = 100) -> pd.DataFrame:
        """
        Coleta as últimas N velas (para uso em tempo real).
        
        Args:
            symbol: Par de trading
            interval: Timeframe
            limit: Número de velas
            
        Returns:
            DataFrame com as últimas velas
        """
        return self.get_historical_klines(symbol=symbol, interval=interval, limit=limit)


# Função de teste
if __name__ == "__main__":
    collector = BinanceDataCollector()
    
    # Teste 1: Coletar últimas 100 velas
    print("Teste 1: Coletando últimas 100 velas M1...")
    df = collector.get_latest_candles(limit=100)
    print(df.head())
    print(f"Shape: {df.shape}")
    
    # Teste 2: Coletar 1 semana de dados
    # print("\nTeste 2: Coletando 1 semana de dados...")
    # start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    # df_week = collector.get_historical_klines(start_date=start, limit=10000)
    # print(f"Shape: {df_week.shape}")
    # print(df_week.tail())

