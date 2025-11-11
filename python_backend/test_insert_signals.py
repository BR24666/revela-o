"""
Script de teste para inserir sinais dummy no banco
Execute este script para testar o frontend antes de rodar o engine completo
"""
from datetime import datetime, timedelta
import random
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

def insert_dummy_signals(count: int = 10):
    """
    Insere sinais dummy no banco para testar o frontend
    """
    print(f"Conectando ao Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print(f"Inserindo {count} sinais de teste...")
    
    base_price = 43250.50
    
    for i in range(count):
        # Timestamp: últimas 2 horas
        minutes_ago = count - i
        timestamp = datetime.now() - timedelta(minutes=minutes_ago * 6)
        
        # Predição aleatória
        prediction = random.choice(['CALL', 'PUT'])
        
        # Confiança: entre 70 e 95%
        confidence = round(random.uniform(70, 95), 2)
        
        # Preço: varia um pouco
        open_price = base_price + random.uniform(-100, 100)
        
        # Resultado: maioria WIN (para simular bom desempenho)
        result_rand = random.random()
        if i < 3:  # Últimos 3 ainda PENDING
            result = 'PENDING'
            close_price = None
        else:
            if result_rand < 0.65:  # 65% de win rate
                result = 'WIN'
                if prediction == 'CALL':
                    close_price = open_price + random.uniform(5, 50)
                else:
                    close_price = open_price - random.uniform(5, 50)
            else:
                result = 'LOSS'
                if prediction == 'CALL':
                    close_price = open_price - random.uniform(5, 30)
                else:
                    close_price = open_price + random.uniform(5, 30)
        
        # Features dummy
        features = {
            'rule_engolfo': random.randint(-1, 1),
            'rule_tres_soldados': random.randint(0, 1),
            'rsi': round(random.uniform(30, 70), 2),
            'ema_diff': round(random.uniform(-50, 50), 2)
        }
        
        # Inserir no banco
        signal_data = {
            'timestamp': timestamp.isoformat(),
            'symbol': 'BTC/USDT',
            'timeframe': 'M1',
            'prediction': prediction,
            'confidence_score': confidence,
            'open_price': open_price,
            'close_price': close_price,
            'result': result,
            'features': features
        }
        
        try:
            supabase.table('signals').insert(signal_data).execute()
            emoji = '🟩' if prediction == 'CALL' else '🟥'
            status_emoji = '✅' if result == 'WIN' else ('❌' if result == 'LOSS' else '⏳')
            print(f"{i+1}. {emoji} {prediction} @ ${open_price:.2f} - {confidence:.1f}% - {status_emoji} {result}")
        except Exception as e:
            print(f"Erro ao inserir sinal {i+1}: {e}")
    
    print(f"\n✅ {count} sinais de teste inseridos com sucesso!")
    print(f"\n📊 Agora acesse o frontend e veja os sinais aparecendo!")


def clear_all_signals():
    """
    Remove todos os sinais do banco (usar com cuidado!)
    """
    print("⚠️  ATENÇÃO: Isso vai remover TODOS os sinais do banco!")
    confirm = input("Digite 'SIM' para confirmar: ")
    
    if confirm == 'SIM':
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        result = supabase.table('signals').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"✅ Todos os sinais foram removidos!")
    else:
        print("❌ Operação cancelada")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("SCRIPT DE TESTE - INSERIR SINAIS DUMMY")
    print("="*60 + "\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        clear_all_signals()
    else:
        # Inserir 15 sinais de teste
        insert_dummy_signals(15)
        
        print("\n" + "="*60)
        print("PRÓXIMOS PASSOS:")
        print("="*60)
        print("1. Acesse o frontend: http://localhost:3000")
        print("2. Veja os sinais na aba 'Sinais'")
        print("3. Veja estatísticas na aba 'Performance'")
        print("\nPara remover todos os sinais: python test_insert_signals.py clear")
        print("="*60 + "\n")

