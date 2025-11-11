"""
Sistema de Machine Learning para previsão de velas
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
from datetime import datetime
from typing import Tuple, Dict
from config import FEATURE_COLUMNS, MODEL_PATH, SCALER_PATH


class MLPredictor:
    """
    Classe responsável por treinar e fazer previsões com modelos de ML.
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = FEATURE_COLUMNS
        
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara os dados para treinamento/previsão.
        
        Args:
            df: DataFrame com features calculadas
            
        Returns:
            Tuple (X, y) com features e target
        """
        # Remover linhas com target NaN
        df_clean = df.dropna(subset=['target'])
        
        # Separar features e target
        X = df_clean[self.feature_columns].values
        y = df_clean['target'].values
        
        return X, y
    
    def train_model(
        self, 
        df: pd.DataFrame, 
        model_type: str = 'xgboost',
        test_size: float = 0.2,
        save_model: bool = True
    ) -> Dict:
        """
        Treina o modelo de ML.
        
        Args:
            df: DataFrame com features calculadas
            model_type: Tipo de modelo ('xgboost', 'random_forest', 'gradient_boosting')
            test_size: Proporção de dados para teste
            save_model: Se True, salva o modelo treinado
            
        Returns:
            Dict com métricas de performance
        """
        print(f"\n{'='*60}")
        print(f"TREINAMENTO DO MODELO - {model_type.upper()}")
        print(f"{'='*60}\n")
        
        # Preparar dados
        X, y = self.prepare_data(df)
        
        print(f"Dataset shape: {X.shape}")
        print(f"Target distribution: Verde={np.sum(y==1)} ({np.sum(y==1)/len(y)*100:.1f}%), "
              f"Vermelha={np.sum(y==0)} ({np.sum(y==0)/len(y)*100:.1f}%)")
        
        # Dividir em treino e teste (respeitando ordem temporal)
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"\nTreino: {len(X_train)} samples")
        print(f"Teste: {len(X_test)} samples")
        
        # Normalizar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Selecionar modelo
        if model_type == 'xgboost':
            self.model = XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric='logloss'
            )
        elif model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42
            )
        else:
            raise ValueError(f"Modelo desconhecido: {model_type}")
        
        # Treinar
        print("\nTreinando modelo...")
        self.model.fit(X_train_scaled, y_train)
        
        # Avaliar
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        train_acc = accuracy_score(y_train, y_pred_train)
        test_acc = accuracy_score(y_test, y_pred_test)
        
        print(f"\n{'='*60}")
        print(f"RESULTADOS DO TREINAMENTO")
        print(f"{'='*60}")
        print(f"\nAccuracy Treino: {train_acc*100:.2f}%")
        print(f"Accuracy Teste: {test_acc*100:.2f}%")
        
        print("\n--- Classification Report (Test Set) ---")
        print(classification_report(y_test, y_pred_test, target_names=['Vermelha', 'Verde']))
        
        print("\n--- Confusion Matrix (Test Set) ---")
        cm = confusion_matrix(y_test, y_pred_test)
        print(f"               Pred Vermelha  Pred Verde")
        print(f"Real Vermelha       {cm[0][0]:6d}      {cm[0][1]:6d}")
        print(f"Real Verde          {cm[1][0]:6d}      {cm[1][1]:6d}")
        
        # Análise por confiança
        print("\n--- Winrate por Nível de Confiança ---")
        y_pred_proba = self.model.predict_proba(X_test_scaled)
        confidence_analysis = self._analyze_by_confidence(y_test, y_pred_test, y_pred_proba)
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            print("\n--- Top 10 Features Mais Importantes ---")
            feature_importance = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            for idx, row in feature_importance.head(10).iterrows():
                print(f"{row['feature']:30s}: {row['importance']:.4f}")
        
        # Salvar modelo
        if save_model:
            self.save_model()
        
        return {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'confidence_analysis': confidence_analysis,
            'model_type': model_type
        }
    
    def _analyze_by_confidence(self, y_true, y_pred, y_proba) -> pd.DataFrame:
        """
        Analisa winrate por faixa de confiança.
        
        Args:
            y_true: Labels verdadeiros
            y_pred: Predições
            y_proba: Probabilidades preditas
            
        Returns:
            DataFrame com análise por confiança
        """
        # Calcular confidence score (max probabilidade)
        confidence = np.max(y_proba, axis=1) * 100
        
        # Criar DataFrame
        df_analysis = pd.DataFrame({
            'true': y_true,
            'pred': y_pred,
            'confidence': confidence,
            'correct': (y_true == y_pred).astype(int)
        })
        
        # Agrupar por faixas de confiança
        bins = [0, 70, 75, 80, 85, 90, 100]
        labels = ['<70%', '70-75%', '75-80%', '80-85%', '85-90%', '90-100%']
        df_analysis['confidence_range'] = pd.cut(df_analysis['confidence'], bins=bins, labels=labels)
        
        # Calcular winrate por faixa
        result = df_analysis.groupby('confidence_range').agg({
            'correct': ['count', 'sum', 'mean']
        }).round(4)
        
        result.columns = ['Total Sinais', 'Wins', 'Winrate']
        result['Winrate'] = result['Winrate'] * 100
        
        print(result)
        
        return result
    
    def predict(self, df: pd.DataFrame) -> Tuple[int, float]:
        """
        Faz previsão para a próxima vela.
        
        Args:
            df: DataFrame com features calculadas (última linha = vela atual)
            
        Returns:
            Tuple (previsão, confiança)
            previsão: 1 (CALL/Verde), 0 (PUT/Vermelha)
            confiança: 0-100 (%)
        """
        if self.model is None:
            raise ValueError("Modelo não foi treinado ou carregado")
        
        # Pegar última linha (vela mais recente)
        X = df[self.feature_columns].iloc[-1:].values
        
        # Normalizar
        X_scaled = self.scaler.transform(X)
        
        # Prever
        prediction = self.model.predict(X_scaled)[0]
        proba = self.model.predict_proba(X_scaled)[0]
        confidence = np.max(proba) * 100
        
        return int(prediction), float(confidence)
    
    def predict_with_details(self, df: pd.DataFrame) -> Dict:
        """
        Faz previsão com informações detalhadas.
        
        Args:
            df: DataFrame com features calculadas
            
        Returns:
            Dict com previsão, confiança, timestamp, preço, etc.
        """
        prediction, confidence = self.predict(df)
        
        last_row = df.iloc[-1]
        
        return {
            'timestamp': last_row['timestamp'],
            'prediction': 'CALL' if prediction == 1 else 'PUT',
            'confidence': confidence,
            'current_price': float(last_row['close']),
            'features': {col: float(last_row[col]) for col in self.feature_columns[:10]}  # Top 10 features
        }
    
    def save_model(self, model_path: str = MODEL_PATH, scaler_path: str = SCALER_PATH):
        """Salva o modelo e scaler treinados."""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        print(f"\n✓ Modelo salvo em: {model_path}")
        print(f"✓ Scaler salvo em: {scaler_path}")
    
    def load_model(self, model_path: str = MODEL_PATH, scaler_path: str = SCALER_PATH):
        """Carrega modelo e scaler previamente treinados."""
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Modelo ou scaler não encontrado em {model_path}")
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        print(f"✓ Modelo carregado de: {model_path}")
        print(f"✓ Scaler carregado de: {scaler_path}")


# Script de treinamento
if __name__ == "__main__":
    from data_collector import BinanceDataCollector
    from feature_engineering import FeatureEngineer
    
    print("\n" + "="*60)
    print("SCRIPT DE TREINAMENTO DO SUPER ANALISTA")
    print("="*60 + "\n")
    
    # 1. Coletar dados históricos
    print("ETAPA 1: Coletando dados históricos...")
    collector = BinanceDataCollector()
    
    # Para testes rápidos, use apenas alguns dias
    # Para produção, use 3-5 anos
    USE_FULL_DATASET = False
    
    if USE_FULL_DATASET:
        df = collector.get_large_historical_dataset(years=3)
    else:
        print("(Modo teste: coletando apenas 30 dias)")
        from datetime import datetime, timedelta
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        df = collector.get_historical_klines(start_date=start_date, limit=50000)
    
    print(f"✓ Dados coletados: {len(df)} velas")
    
    # 2. Calcular features
    print("\nETAPA 2: Calculando features...")
    engineer = FeatureEngineer(df)
    features_df = engineer.calculate_all_features()
    
    print(f"✓ Features calculadas: {features_df.shape}")
    
    # 3. Treinar modelo
    print("\nETAPA 3: Treinando modelo...")
    predictor = MLPredictor()
    results = predictor.train_model(features_df, model_type='xgboost', test_size=0.2)
    
    print("\n" + "="*60)
    print("TREINAMENTO CONCLUÍDO!")
    print("="*60)
    print(f"\nTest Accuracy: {results['test_accuracy']*100:.2f}%")
    print("\nO modelo está pronto para ser usado em produção.")
    print(f"Arquivos salvos em: ml_models/")

