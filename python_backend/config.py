"""
Configurações do sistema
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', 'https://utmouqkyveodxrkqyies.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

# Binance
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')

# Trading
SYMBOL = 'BTCUSDT'
TIMEFRAME = '1m'
LOOKBACK_PERIODS = 100  # Quantas velas usar para cálculo de features

# Machine Learning
MIN_CONFIDENCE_THRESHOLD = 70.0  # Mínimo de confiança para gerar sinal
MODEL_PATH = 'ml_models/trained_model.pkl'
SCALER_PATH = 'ml_models/scaler.pkl'

# Features
FEATURE_COLUMNS = [
    # Regras Probabilísticas (10)
    'rule_engolfo',
    'rule_tres_soldados',
    'rule_vela_forca',
    'rule_tres_vales_picos',
    'rule_mhi',
    'rule_reversao_doji',
    'rule_minoria',
    'rule_primeira_quadrante',
    'rule_alternancia',
    'rule_sequencia_impar',
    
    # Indicadores Técnicos
    'rsi',
    'rsi_oversold',
    'rsi_overbought',
    'ema_9',
    'ema_21',
    'ema_diff',
    'price_above_ema9',
    'price_above_ema21',
    'bb_upper',
    'bb_middle',
    'bb_lower',
    'bb_width',
    'bb_position',
    
    # Price Action
    'distance_to_high',
    'distance_to_low',
    'pivot_structure',
    'upper_wick_pct',
    'lower_wick_pct',
    'body_size_pct',
]

# Horários e dias de maior assertividade (baseado nas regras)
BEST_HOURS = {
    'rule_engolfo': 8,
    'rule_tres_soldados': 14,
    'rule_vela_forca': 13,
    'rule_tres_vales_picos': 12,
    'rule_mhi': 10,
    'rule_reversao_doji': 15,
    'rule_minoria': 9,
    'rule_primeira_quadrante': 10,
    'rule_alternancia': 11,
    'rule_sequencia_impar': 9,
}

BEST_DAYS = {
    'rule_engolfo': 5,  # Sábado
    'rule_tres_soldados': 2,  # Quarta
    'rule_vela_forca': 4,  # Sexta
    'rule_tres_vales_picos': 2,  # Quarta
    'rule_mhi': 0,  # Segunda
    'rule_reversao_doji': 0,  # Segunda
    'rule_minoria': 1,  # Terça
    'rule_primeira_quadrante': 6,  # Domingo
    'rule_alternancia': 3,  # Quinta
    'rule_sequencia_impar': 1,  # Terça
}

