"""
Engine de tempo real - WebSocket + Previsões
"""
import asyncio
import websockets
import json
from datetime import datetime
import pandas as pd
from typing import Dict, Optional
from data_collector import BinanceDataCollector
from feature_engineering import FeatureEngineer
from ml_model import MLPredictor
from config import SYMBOL, TIMEFRAME, MIN_CONFIDENCE_THRESHOLD, LOOKBACK_PERIODS
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY


class RealtimeEngine:
    """
    Engine que processa dados em tempo real via WebSocket da Binance
    e gera sinais quando o modelo atinge confiança suficiente.
    """
    
    def __init__(self):
        self.collector = BinanceDataCollector()
        self.predictor = MLPredictor()
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Cache de velas recentes
        self.candles_buffer = []
        self.last_prediction = None
        
        # Carregar modelo treinado
        try:
            self.predictor.load_model()
            print("✓ Modelo carregado com sucesso")
        except Exception as e:
            print(f"⚠ Erro ao carregar modelo: {e}")
            print("Execute python_backend/ml_model.py primeiro para treinar o modelo")
    
    async def start(self):
        """Inicia o engine de tempo real."""
        print("\n" + "="*60)
        print("SUPER ANALISTA - ENGINE DE TEMPO REAL")
        print("="*60 + "\n")
        
        # Inicializar buffer com dados históricos
        print("Inicializando buffer com dados históricos...")
        await self._init_buffer()
        
        # Conectar ao WebSocket da Binance
        symbol = SYMBOL.lower()
        ws_url = f"wss://stream.binance.com:9443/ws/{symbol}@kline_{TIMEFRAME}"
        
        print(f"Conectando ao WebSocket: {ws_url}\n")
        
        async with websockets.connect(ws_url) as websocket:
            print("✓ Conectado! Aguardando velas...\n")
            
            async for message in websocket:
                await self._process_message(message)
    
    async def _init_buffer(self):
        """Inicializa o buffer com as últimas N velas."""
        df = self.collector.get_latest_candles(limit=LOOKBACK_PERIODS)
        self.candles_buffer = df.to_dict('records')
        print(f"✓ Buffer inicializado com {len(self.candles_buffer)} velas")
    
    async def _process_message(self, message: str):
        """Processa mensagem do WebSocket."""
        data = json.loads(message)
        
        if 'k' not in data:
            return
        
        kline = data['k']
        is_closed = kline['x']  # True se a vela fechou
        
        # Atualizar vela atual no buffer
        current_candle = {
            'timestamp': pd.to_datetime(kline['t'], unit='ms'),
            'open': float(kline['o']),
            'high': float(kline['h']),
            'low': float(kline['l']),
            'close': float(kline['c']),
            'volume': float(kline['v'])
        }
        
        # Apenas quando a vela fecha
        if is_closed:
            print(f"\n{'='*60}")
            print(f"NOVA VELA FECHADA - {current_candle['timestamp']}")
            print(f"{'='*60}")
            print(f"O: {current_candle['open']:.2f} | H: {current_candle['high']:.2f} | "
                  f"L: {current_candle['low']:.2f} | C: {current_candle['close']:.2f}")
            
            # Adicionar ao buffer
            self.candles_buffer.append(current_candle)
            
            # Manter apenas as últimas N velas
            if len(self.candles_buffer) > LOOKBACK_PERIODS:
                self.candles_buffer.pop(0)
            
            # Fazer previsão
            await self._make_prediction()
    
    async def _make_prediction(self):
        """Faz previsão com os dados atuais."""
        try:
            # Converter buffer para DataFrame
            df = pd.DataFrame(self.candles_buffer)
            
            # Calcular features
            engineer = FeatureEngineer(df)
            features_df = engineer.calculate_all_features()
            
            if len(features_df) == 0:
                print("⚠ Features insuficientes para previsão")
                return
            
            # Fazer previsão
            prediction_details = self.predictor.predict_with_details(features_df)
            
            prediction = prediction_details['prediction']
            confidence = prediction_details['confidence']
            
            print(f"\n--- PREVISÃO ---")
            print(f"Direção: {prediction} ({'🟩 CALL' if prediction == 'CALL' else '🟥 PUT'})")
            print(f"Confiança: {confidence:.2f}%")
            
            # Verificar se atinge o limiar mínimo
            if confidence >= MIN_CONFIDENCE_THRESHOLD:
                print(f"\n✓ SINAL GERADO! (Confiança acima de {MIN_CONFIDENCE_THRESHOLD}%)")
                await self._save_signal(prediction_details)
            else:
                print(f"\n⚠ Confiança abaixo do limiar ({MIN_CONFIDENCE_THRESHOLD}%). Sinal não gerado.")
            
            self.last_prediction = prediction_details
            
        except Exception as e:
            print(f"Erro ao fazer previsão: {e}")
            import traceback
            traceback.print_exc()
    
    async def _save_signal(self, prediction_details: Dict):
        """Salva sinal no Supabase."""
        try:
            signal_data = {
                'timestamp': prediction_details['timestamp'].isoformat(),
                'symbol': 'BTC/USDT',
                'timeframe': 'M1',
                'prediction': prediction_details['prediction'],
                'confidence_score': prediction_details['confidence'],
                'open_price': prediction_details['current_price'],
                'result': 'PENDING',
                'features': prediction_details['features']
            }
            
            result = self.supabase.table('signals').insert(signal_data).execute()
            
            print(f"✓ Sinal salvo no banco de dados (ID: {result.data[0]['id']})")
            
            # Agendar verificação de resultado em 60 segundos
            asyncio.create_task(self._verify_signal_result(result.data[0]['id'], prediction_details))
            
        except Exception as e:
            print(f"Erro ao salvar sinal: {e}")
    
    async def _verify_signal_result(self, signal_id: str, prediction_details: Dict):
        """
        Verifica o resultado do sinal após 60 segundos.
        """
        await asyncio.sleep(65)  # Aguardar 65 segundos (vela fechar + margem)
        
        try:
            # Buscar preço de fechamento atual
            df = self.collector.get_latest_candles(limit=2)
            close_price = float(df.iloc[-1]['close'])
            
            open_price = prediction_details['current_price']
            prediction = prediction_details['prediction']
            
            # Determinar resultado
            if prediction == 'CALL':
                result = 'WIN' if close_price > open_price else 'LOSS'
            else:  # PUT
                result = 'WIN' if close_price < open_price else 'LOSS'
            
            # Atualizar no banco
            self.supabase.table('signals').update({
                'close_price': close_price,
                'result': result
            }).eq('id', signal_id).execute()
            
            emoji = '✅' if result == 'WIN' else '❌'
            print(f"\n{emoji} Resultado do sinal {signal_id}: {result}")
            print(f"   Open: {open_price:.2f} | Close: {close_price:.2f} | Diff: {close_price - open_price:.2f}")
            
        except Exception as e:
            print(f"Erro ao verificar resultado: {e}")


# Script de execução
async def main():
    engine = RealtimeEngine()
    await engine.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✓ Engine finalizado pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

