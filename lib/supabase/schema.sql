-- Schema para o Super Analista BTC/USDT
-- Execute este script no SQL Editor do Supabase

-- Tabela de sinais gerados pela IA
CREATE TABLE IF NOT EXISTS signals (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  symbol VARCHAR(20) NOT NULL DEFAULT 'BTC/USDT',
  timeframe VARCHAR(10) NOT NULL DEFAULT 'M1',
  prediction VARCHAR(10) NOT NULL CHECK (prediction IN ('CALL', 'PUT')),
  confidence_score DECIMAL(5,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
  open_price DECIMAL(20,8) NOT NULL,
  close_price DECIMAL(20,8),
  result VARCHAR(10) CHECK (result IN ('WIN', 'LOSS', 'PENDING')),
  features JSONB
);

-- Índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_signals_result ON signals(result);
CREATE INDEX IF NOT EXISTS idx_signals_confidence ON signals(confidence_score);

-- Tabela de estatísticas de performance
CREATE TABLE IF NOT EXISTS performance_stats (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  period VARCHAR(50) NOT NULL,
  total_signals INTEGER NOT NULL DEFAULT 0,
  wins INTEGER NOT NULL DEFAULT 0,
  losses INTEGER NOT NULL DEFAULT 0,
  winrate DECIMAL(5,2) NOT NULL DEFAULT 0,
  confidence_range VARCHAR(20) NOT NULL,
  avg_confidence DECIMAL(5,2) NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_performance_period ON performance_stats(period);
CREATE INDEX IF NOT EXISTS idx_performance_confidence_range ON performance_stats(confidence_range);

-- Tabela de configurações do usuário
CREATE TABLE IF NOT EXISTS user_settings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL UNIQUE,
  min_confidence_threshold DECIMAL(5,2) NOT NULL DEFAULT 75.0,
  notification_enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de dados de mercado (cache)
CREATE TABLE IF NOT EXISTS market_data (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  symbol VARCHAR(20) NOT NULL DEFAULT 'BTC/USDT',
  timeframe VARCHAR(10) NOT NULL DEFAULT 'M1',
  open DECIMAL(20,8) NOT NULL,
  high DECIMAL(20,8) NOT NULL,
  low DECIMAL(20,8) NOT NULL,
  close DECIMAL(20,8) NOT NULL,
  volume DECIMAL(20,8) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(timestamp, symbol, timeframe)
);

CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol, timeframe);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para user_settings
CREATE TRIGGER update_user_settings_updated_at 
  BEFORE UPDATE ON user_settings 
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

-- View para estatísticas agregadas
CREATE OR REPLACE VIEW signal_statistics AS
SELECT 
  DATE_TRUNC('hour', timestamp) as hour,
  COUNT(*) as total_signals,
  SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
  SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
  ROUND(AVG(CASE WHEN result = 'WIN' THEN 100 ELSE 0 END), 2) as winrate,
  ROUND(AVG(confidence_score), 2) as avg_confidence
FROM signals
WHERE result IN ('WIN', 'LOSS')
GROUP BY hour
ORDER BY hour DESC;

-- Função para calcular winrate por faixa de confiança
CREATE OR REPLACE FUNCTION calculate_winrate_by_confidence()
RETURNS TABLE (
  confidence_range TEXT,
  total_signals BIGINT,
  wins BIGINT,
  losses BIGINT,
  winrate NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    CASE 
      WHEN confidence_score >= 90 THEN '90-100%'
      WHEN confidence_score >= 80 THEN '80-90%'
      WHEN confidence_score >= 75 THEN '75-80%'
      WHEN confidence_score >= 70 THEN '70-75%'
      ELSE '< 70%'
    END as confidence_range,
    COUNT(*) as total_signals,
    SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'LOSS' THEN 1 ELSE 0 END) as losses,
    ROUND(AVG(CASE WHEN result = 'WIN' THEN 100 ELSE 0 END), 2) as winrate
  FROM signals
  WHERE result IN ('WIN', 'LOSS')
  GROUP BY confidence_range
  ORDER BY confidence_range DESC;
END;
$$ LANGUAGE plpgsql;

-- Habilitar Row Level Security (RLS)
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;

-- Políticas de acesso (permitir leitura pública, escrita apenas pelo service role)
CREATE POLICY "Allow public read access on signals" ON signals FOR SELECT USING (true);
CREATE POLICY "Allow public read access on performance_stats" ON performance_stats FOR SELECT USING (true);
CREATE POLICY "Allow public read access on market_data" ON market_data FOR SELECT USING (true);
CREATE POLICY "Allow users to read their own settings" ON user_settings FOR SELECT USING (true);
CREATE POLICY "Allow users to update their own settings" ON user_settings FOR UPDATE USING (true);
CREATE POLICY "Allow users to insert their own settings" ON user_settings FOR INSERT WITH CHECK (true);

