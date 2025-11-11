"""
Engenharia de Features - Cálculo de todos os indicadores e regras
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
import ta
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


class FeatureEngineer:
    """
    Classe responsável por calcular todas as features necessárias:
    - 10 Regras Probabilísticas
    - Indicadores Técnicos (RSI, EMA, Bollinger)
    - Price Action (S/R, Pivots, Wicks)
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa com um DataFrame de velas OHLCV.
        
        Args:
            df: DataFrame com colunas [timestamp, open, high, low, close, volume]
        """
        self.df = df.copy()
        self.features_df = df.copy()
    
    def calculate_all_features(self) -> pd.DataFrame:
        """
        Calcula todas as features de uma vez.
        
        Returns:
            DataFrame com todas as features calculadas
        """
        print("Calculando features...")
        
        # Adicionar coluna de cor da vela
        self.features_df['color'] = (self.features_df['close'] > self.features_df['open']).astype(int)
        # 1 = Verde (alta), 0 = Vermelha (baixa)
        
        # Adicionar target (cor da próxima vela)
        self.features_df['target'] = self.features_df['color'].shift(-1)
        
        # Calcular todas as categorias de features
        self._calculate_probabilistic_rules()
        self._calculate_technical_indicators()
        self._calculate_price_action()
        
        # Remover linhas com NaN (primeiras linhas não têm dados suficientes)
        self.features_df = self.features_df.dropna()
        
        print(f"✓ Features calculadas. Shape: {self.features_df.shape}")
        
        return self.features_df
    
    # ========== PILAR 1: REGRAS PROBABILÍSTICAS (10 REGRAS) ==========
    
    def _calculate_probabilistic_rules(self):
        """Calcula as 10 regras probabilísticas como features."""
        
        # 1. Engolfo de Cor Única (92.9%)
        self.features_df['rule_engolfo'] = self._rule_engolfo()
        
        # 2. Três Soldados Brancos (92.0%)
        self.features_df['rule_tres_soldados'] = self._rule_tres_soldados()
        
        # 3. Vela de Força (90.9%)
        self.features_df['rule_vela_forca'] = self._rule_vela_forca()
        
        # 4. Três Vales/Picos (85.7%)
        self.features_df['rule_tres_vales_picos'] = self._rule_tres_vales_picos()
        
        # 5. MHI (85.0%)
        self.features_df['rule_mhi'] = self._rule_mhi()
        
        # 6. Reversão Pós-Doji (84.2%)
        self.features_df['rule_reversao_doji'] = self._rule_reversao_doji()
        
        # 7. Minoria (80.0%)
        self.features_df['rule_minoria'] = self._rule_minoria()
        
        # 8. Primeira Vela do Quadrante (75.0%)
        self.features_df['rule_primeira_quadrante'] = self._rule_primeira_quadrante()
        
        # 9. Alternância de Cores (72.2%)
        self.features_df['rule_alternancia'] = self._rule_alternancia()
        
        # 10. Sequência Ímpar (71.4%)
        self.features_df['rule_sequencia_impar'] = self._rule_sequencia_impar()
    
    def _rule_engolfo(self) -> pd.Series:
        """
        Engolfo de Cor Única: Vela grande engolfa a anterior e mantém a mesma cor.
        Retorna: 1 (CALL), -1 (PUT), 0 (neutro)
        """
        df = self.features_df
        
        # Tamanho do corpo
        body = abs(df['close'] - df['open'])
        prev_body = body.shift(1)
        
        # Engolfo de alta: vela verde engolfa vela anterior
        engolfo_alta = (
            (df['color'] == 1) &  # Vela atual verde
            (df['color'].shift(1) == 1) &  # Vela anterior também verde
            (body > prev_body * 1.5) &  # Corpo atual 50% maior
            (df['low'] <= df['low'].shift(1)) &  # Low engolfa
            (df['high'] >= df['high'].shift(1))  # High engolfa
        )
        
        # Engolfo de baixa: vela vermelha engolfa vela anterior
        engolfo_baixa = (
            (df['color'] == 0) &  # Vela atual vermelha
            (df['color'].shift(1) == 0) &  # Vela anterior também vermelha
            (body > prev_body * 1.5) &
            (df['low'] <= df['low'].shift(1)) &
            (df['high'] >= df['high'].shift(1))
        )
        
        result = pd.Series(0, index=df.index)
        result[engolfo_alta] = 1
        result[engolfo_baixa] = -1
        
        return result
    
    def _rule_tres_soldados(self) -> pd.Series:
        """
        Três Soldados Brancos: Três velas consecutivas de alta.
        Retorna: 1 (CALL esperado), 0 (neutro)
        """
        df = self.features_df
        
        tres_soldados = (
            (df['color'] == 1) &
            (df['color'].shift(1) == 1) &
            (df['color'].shift(2) == 1) &
            (df['close'] > df['close'].shift(1)) &
            (df['close'].shift(1) > df['close'].shift(2))
        )
        
        return tres_soldados.astype(int)
    
    def _rule_vela_forca(self) -> pd.Series:
        """
        Vela de Força: Corpo grande e pavio curto.
        Retorna: 1 (CALL), -1 (PUT), 0 (neutro)
        """
        df = self.features_df
        
        body = abs(df['close'] - df['open'])
        total_range = df['high'] - df['low']
        
        # Vela forte quando corpo ocupa >70% da range total
        vela_forte = body / (total_range + 1e-10) > 0.7
        
        result = pd.Series(0, index=df.index)
        result[vela_forte & (df['color'] == 1)] = 1  # Verde forte
        result[vela_forte & (df['color'] == 0)] = -1  # Vermelha forte
        
        return result
    
    def _rule_tres_vales_picos(self) -> pd.Series:
        """
        Três Vales/Picos: Formação de três fundos ascendentes ou topos descendentes.
        Retorna: 1 (vales - compra), -1 (picos - venda), 0 (neutro)
        """
        df = self.features_df
        
        # Vales ascendentes (três fundos subindo)
        vales = (
            (df['low'] > df['low'].shift(1)) &
            (df['low'].shift(1) > df['low'].shift(2))
        )
        
        # Picos descendentes (três topos descendo)
        picos = (
            (df['high'] < df['high'].shift(1)) &
            (df['high'].shift(1) < df['high'].shift(2))
        )
        
        result = pd.Series(0, index=df.index)
        result[vales] = 1
        result[picos] = -1
        
        return result
    
    def _rule_mhi(self) -> pd.Series:
        """
        MHI: Analisa últimas 3 velas, se 2+ da mesma cor, entra na cor oposta.
        Retorna: 1 (CALL), -1 (PUT), 0 (neutro)
        """
        df = self.features_df
        
        # Contar cores nas últimas 3 velas
        last_3_sum = df['color'] + df['color'].shift(1) + df['color'].shift(2)
        
        # Se sum >= 2, maioria verde → sinal PUT (-1)
        # Se sum <= 1, maioria vermelha → sinal CALL (1)
        result = pd.Series(0, index=df.index)
        result[last_3_sum >= 2] = -1  # Maioria verde, entrar PUT
        result[last_3_sum <= 1] = 1   # Maioria vermelha, entrar CALL
        
        return result
    
    def _rule_reversao_doji(self) -> pd.Series:
        """
        Reversão Pós-Doji: Após Doji, reversão na direção contrária.
        Retorna: 1 (CALL), -1 (PUT), 0 (neutro)
        """
        df = self.features_df
        
        body = abs(df['close'] - df['open'])
        total_range = df['high'] - df['low']
        
        # Doji: corpo pequeno (<20% da range total)
        is_doji = body / (total_range + 1e-10) < 0.2
        
        # Reversão após doji
        doji_anterior = is_doji.shift(1)
        
        result = pd.Series(0, index=df.index)
        result[doji_anterior & (df['color'] == 1)] = 1   # Após doji, vela verde
        result[doji_anterior & (df['color'] == 0)] = -1  # Após doji, vela vermelha
        
        return result
    
    def _rule_minoria(self) -> pd.Series:
        """
        Minoria: Nas últimas 3 velas, entra a favor da cor minoritária.
        Retorna: 1 (CALL), -1 (PUT), 0 (neutro)
        """
        df = self.features_df
        
        last_3_sum = df['color'] + df['color'].shift(1) + df['color'].shift(2)
        
        # Se exatamente 1 verde (minority), sinal CALL
        # Se exatamente 2 verdes (1 vermelha minority), sinal PUT
        result = pd.Series(0, index=df.index)
        result[last_3_sum == 1] = 1   # 1 verde, 2 vermelhas → entrar CALL
        result[last_3_sum == 2] = -1  # 2 verdes, 1 vermelha → entrar PUT
        
        return result
    
    def _rule_primeira_quadrante(self) -> pd.Series:
        """
        Primeira Vela do Quadrante: Se primeira vela de um bloco é forte, continua nessa direção.
        (Simplificado: verificar se é primeira vela de cada hora)
        Retorna: 1 (CALL), -1 (PUT), 0 (neutro)
        """
        df = self.features_df
        
        # Identificar se é primeira vela de cada 15 minutos
        df_temp = df.copy()
        df_temp['minute'] = pd.to_datetime(df_temp['timestamp']).dt.minute
        is_first_of_quadrant = df_temp['minute'] % 15 == 0
        
        body = abs(df['close'] - df['open'])
        total_range = df['high'] - df['low']
        vela_forte = body / (total_range + 1e-10) > 0.6
        
        result = pd.Series(0, index=df.index)
        result[is_first_of_quadrant & vela_forte & (df['color'] == 1)] = 1
        result[is_first_of_quadrant & vela_forte & (df['color'] == 0)] = -1
        
        return result
    
    def _rule_alternancia(self) -> pd.Series:
        """
        Alternância de Cores: Sequência alternada (verde, vermelha, verde...).
        Retorna: 1 (próxima verde), -1 (próxima vermelha), 0 (sem padrão)
        """
        df = self.features_df
        
        # Verificar alternância nas últimas 3
        alternancia = (
            (df['color'] != df['color'].shift(1)) &
            (df['color'].shift(1) != df['color'].shift(2))
        )
        
        # Próxima cor esperada é oposta à atual
        result = pd.Series(0, index=df.index)
        result[alternancia & (df['color'] == 1)] = -1  # Atual verde, próxima vermelha
        result[alternancia & (df['color'] == 0)] = 1   # Atual vermelha, próxima verde
        
        return result
    
    def _rule_sequencia_impar(self) -> pd.Series:
        """
        Sequência Ímpar: Após 3 velas iguais, entra contra a sequência.
        Retorna: 1 (CALL), -1 (PUT), 0 (neutro)
        """
        df = self.features_df
        
        # Três velas verdes seguidas
        tres_verdes = (
            (df['color'] == 1) &
            (df['color'].shift(1) == 1) &
            (df['color'].shift(2) == 1)
        )
        
        # Três velas vermelhas seguidas
        tres_vermelhas = (
            (df['color'] == 0) &
            (df['color'].shift(1) == 0) &
            (df['color'].shift(2) == 0)
        )
        
        result = pd.Series(0, index=df.index)
        result[tres_verdes] = -1  # Após 3 verdes, entra PUT
        result[tres_vermelhas] = 1  # Após 3 vermelhas, entra CALL
        
        return result
    
    # ========== PILAR 2: INDICADORES TÉCNICOS ==========
    
    def _calculate_technical_indicators(self):
        """Calcula indicadores técnicos padrão."""
        df = self.features_df
        
        # RSI (14 períodos)
        rsi_indicator = RSIIndicator(close=df['close'], window=14)
        df['rsi'] = rsi_indicator.rsi()
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        
        # EMAs
        ema9 = EMAIndicator(close=df['close'], window=9)
        ema21 = EMAIndicator(close=df['close'], window=21)
        
        df['ema_9'] = ema9.ema_indicator()
        df['ema_21'] = ema21.ema_indicator()
        df['ema_diff'] = df['ema_9'] - df['ema_21']
        df['price_above_ema9'] = (df['close'] > df['ema_9']).astype(int)
        df['price_above_ema21'] = (df['close'] > df['ema_21']).astype(int)
        
        # Bollinger Bands
        bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        
        # Posição do preço na banda (0 = na lower, 1 = na upper)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_width'] + 1e-10)
        
        self.features_df = df
    
    # ========== PILAR 3: PRICE ACTION ==========
    
    def _calculate_price_action(self):
        """Calcula features de estrutura de preço."""
        df = self.features_df
        
        # Suporte e Resistência (distância em % das últimas 50 velas)
        rolling_high = df['high'].rolling(window=50).max()
        rolling_low = df['low'].rolling(window=50).min()
        
        df['distance_to_high'] = (rolling_high - df['close']) / (df['close'] + 1e-10)
        df['distance_to_low'] = (df['close'] - rolling_low) / (df['close'] + 1e-10)
        
        # Estrutura de Pivots (simplificado: comparar closes recentes)
        df['pivot_structure'] = (
            (df['close'] > df['close'].shift(5)).astype(int) * 2 +
            (df['close'] > df['close'].shift(10)).astype(int) * 1 -
            (df['close'] < df['close'].shift(5)).astype(int) * 2 -
            (df['close'] < df['close'].shift(10)).astype(int) * 1
        )
        # Resultado: +2 (forte alta), 0 (lateral), -2 (forte baixa)
        
        # Análise de Pavios (Wicks)
        body = abs(df['close'] - df['open'])
        upper_wick = df['high'] - df[['open', 'close']].max(axis=1)
        lower_wick = df[['open', 'close']].min(axis=1) - df['low']
        total_range = df['high'] - df['low']
        
        df['upper_wick_pct'] = upper_wick / (total_range + 1e-10)
        df['lower_wick_pct'] = lower_wick / (total_range + 1e-10)
        df['body_size_pct'] = body / (total_range + 1e-10)
        
        self.features_df = df


# Função de teste
if __name__ == "__main__":
    from data_collector import BinanceDataCollector
    
    print("Teste do Feature Engineer...")
    
    # Coletar dados
    collector = BinanceDataCollector()
    df = collector.get_latest_candles(limit=200)
    
    # Calcular features
    engineer = FeatureEngineer(df)
    features_df = engineer.calculate_all_features()
    
    print("\n=== Features Calculadas ===")
    print(features_df.tail(10))
    
    print("\n=== Colunas ===")
    print(features_df.columns.tolist())
    
    print(f"\n=== Shape: {features_df.shape} ===")

