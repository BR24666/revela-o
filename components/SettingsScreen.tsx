'use client'

import { useState, useEffect } from 'react'
import { Settings, Save, AlertCircle } from 'lucide-react'

export default function SettingsScreen() {
  const [minConfidence, setMinConfidence] = useState(75)
  const [notification, setNotification] = useState(true)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    // Carregar configurações do localStorage
    const savedConfidence = localStorage.getItem('minConfidence')
    const savedNotification = localStorage.getItem('notification')

    if (savedConfidence) setMinConfidence(Number(savedConfidence))
    if (savedNotification) setNotification(savedNotification === 'true')
  }, [])

  function handleSave() {
    localStorage.setItem('minConfidence', minConfidence.toString())
    localStorage.setItem('notification', notification.toString())
    
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="card">
        <div className="flex items-center gap-2 mb-6">
          <Settings className="text-blue-500" />
          <h2 className="text-xl font-semibold">Configurações</h2>
        </div>

        <div className="space-y-6">
          {/* Nível de Confiança Mínimo */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Nível de Confiança Mínimo
            </label>
            <p className="text-sm text-gray-400 mb-4">
              Apenas sinais com confiança igual ou superior a este valor serão exibidos
            </p>
            
            <div className="space-y-3">
              <input
                type="range"
                min="50"
                max="95"
                step="5"
                value={minConfidence}
                onChange={(e) => setMinConfidence(Number(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
              
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-blue-500">{minConfidence}%</span>
                
                <div className="text-sm text-gray-400">
                  {minConfidence >= 85 && '🔥 Muito Alto'}
                  {minConfidence >= 75 && minConfidence < 85 && '✅ Alto'}
                  {minConfidence >= 65 && minConfidence < 75 && '⚖️ Moderado'}
                  {minConfidence < 65 && '⚠️ Baixo'}
                </div>
              </div>
            </div>
          </div>

          {/* Notificações */}
          <div className="flex items-center justify-between py-4 border-t border-[var(--border)]">
            <div>
              <p className="font-medium">Notificações</p>
              <p className="text-sm text-gray-400">Receber alertas de novos sinais</p>
            </div>
            
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notification}
                onChange={(e) => setNotification(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {/* Botão Salvar */}
          <button
            onClick={handleSave}
            className="w-full btn-primary flex items-center justify-center gap-2 mt-6"
          >
            <Save size={20} />
            Salvar Configurações
          </button>

          {saved && (
            <div className="flex items-center gap-2 p-4 bg-green-500/20 border border-green-500/50 rounded-lg text-green-400">
              <AlertCircle size={20} />
              <span>Configurações salvas com sucesso!</span>
            </div>
          )}
        </div>
      </div>

      {/* Informações */}
      <div className="card bg-blue-500/5 border-blue-500/30">
        <h3 className="font-semibold mb-3 text-blue-400">ℹ️ Sobre o Sistema</h3>
        <div className="text-sm text-gray-300 space-y-2">
          <p>
            <strong>Super Analista</strong> utiliza Machine Learning para prever a direção 
            da próxima vela de 1 minuto (M1) no par BTC/USDT.
          </p>
          <p>
            O sistema analisa <strong>10 regras probabilísticas</strong>, <strong>indicadores técnicos</strong> (RSI, EMA, Bollinger) 
            e <strong>price action</strong> para gerar sinais com score de confiança.
          </p>
          <p className="text-yellow-400">
            ⚠️ Este sistema é apenas uma ferramenta de assistência. Não é um bot de trade automático.
            Sempre faça sua própria análise antes de operar.
          </p>
        </div>
      </div>

      {/* Estatísticas do Modelo */}
      <div className="card">
        <h3 className="font-semibold mb-3">📊 Informações do Modelo</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-400">Algoritmo</p>
            <p className="font-semibold">XGBoost</p>
          </div>
          <div>
            <p className="text-gray-400">Features</p>
            <p className="font-semibold">30+ indicadores</p>
          </div>
          <div>
            <p className="text-gray-400">Timeframe</p>
            <p className="font-semibold">M1 (1 minuto)</p>
          </div>
          <div>
            <p className="text-gray-400">Ativo</p>
            <p className="font-semibold">BTC/USDT</p>
          </div>
        </div>
      </div>
    </div>
  )
}

