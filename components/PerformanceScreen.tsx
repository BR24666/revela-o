'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase/client'
import { TrendingUp, TrendingDown, Target, Percent } from 'lucide-react'

interface Stats {
  total: number
  wins: number
  losses: number
  winrate: number
}

interface ConfidenceStats {
  range: string
  total: number
  wins: number
  winrate: number
}

export default function PerformanceScreen() {
  const [overallStats, setOverallStats] = useState<Stats>({ total: 0, wins: 0, losses: 0, winrate: 0 })
  const [confidenceStats, setConfidenceStats] = useState<ConfidenceStats[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadPerformanceData()

    // Atualizar a cada 30 segundos
    const interval = setInterval(loadPerformanceData, 30000)
    return () => clearInterval(interval)
  }, [])

  async function loadPerformanceData() {
    try {
      setLoading(true)

      // Buscar todos os sinais com resultado
      const { data: signals, error } = await supabase
        .from('signals')
        .select('*')
        .in('result', ['WIN', 'LOSS'])
        .order('timestamp', { ascending: false })

      if (error) throw error

      if (!signals || signals.length === 0) {
        setLoading(false)
        return
      }

      // Calcular estatísticas gerais
      const wins = signals.filter(s => s.result === 'WIN').length
      const losses = signals.filter(s => s.result === 'LOSS').length
      const total = signals.length
      const winrate = total > 0 ? (wins / total) * 100 : 0

      setOverallStats({ total, wins, losses, winrate })

      // Calcular por faixa de confiança
      const ranges = [
        { label: '90-100%', min: 90, max: 100 },
        { label: '85-90%', min: 85, max: 90 },
        { label: '80-85%', min: 80, max: 85 },
        { label: '75-80%', min: 75, max: 80 },
        { label: '70-75%', min: 70, max: 75 },
        { label: '< 70%', min: 0, max: 70 },
      ]

      const confidenceData: ConfidenceStats[] = ranges.map(range => {
        const filtered = signals.filter(
          s => s.confidence_score >= range.min && s.confidence_score < range.max
        )
        const rangeWins = filtered.filter(s => s.result === 'WIN').length
        const rangeTotal = filtered.length
        const rangeWinrate = rangeTotal > 0 ? (rangeWins / rangeTotal) * 100 : 0

        return {
          range: range.label,
          total: rangeTotal,
          wins: rangeWins,
          winrate: rangeWinrate
        }
      }).filter(stat => stat.total > 0) // Apenas mostrar faixas com dados

      setConfidenceStats(confidenceData)

    } catch (error) {
      console.error('Erro ao carregar performance:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Carregando estatísticas...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Cards de Estatísticas Gerais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card bg-blue-500/10 border-blue-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Total de Sinais</p>
              <p className="text-3xl font-bold mt-1">{overallStats.total}</p>
            </div>
            <Target size={32} className="text-blue-500" />
          </div>
        </div>

        <div className="card bg-green-500/10 border-green-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Acertos</p>
              <p className="text-3xl font-bold mt-1 text-green-500">{overallStats.wins}</p>
            </div>
            <TrendingUp size={32} className="text-green-500" />
          </div>
        </div>

        <div className="card bg-red-500/10 border-red-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Erros</p>
              <p className="text-3xl font-bold mt-1 text-red-500">{overallStats.losses}</p>
            </div>
            <TrendingDown size={32} className="text-red-500" />
          </div>
        </div>

        <div className="card bg-purple-500/10 border-purple-500/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Winrate</p>
              <p className="text-3xl font-bold mt-1 text-purple-500">
                {overallStats.winrate.toFixed(1)}%
              </p>
            </div>
            <Percent size={32} className="text-purple-500" />
          </div>
        </div>
      </div>

      {/* Winrate por Faixa de Confiança */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Winrate por Nível de Confiança</h3>
        
        {confidenceStats.length > 0 ? (
          <div className="space-y-4">
            {confidenceStats.map((stat) => (
              <div key={stat.range} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{stat.range}</span>
                  <div className="flex items-center gap-4 text-gray-400">
                    <span>{stat.wins}/{stat.total}</span>
                    <span className="font-bold text-white">{stat.winrate.toFixed(1)}%</span>
                  </div>
                </div>
                
                {/* Barra de progresso */}
                <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-500 ${
                      stat.winrate >= 60 ? 'bg-green-500' :
                      stat.winrate >= 50 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${stat.winrate}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-gray-500 py-8">
            Sem dados suficientes ainda
          </p>
        )}
      </div>

      {/* Insights */}
      {confidenceStats.length > 0 && (
        <div className="card bg-blue-500/5 border-blue-500/30">
          <h3 className="text-lg font-semibold mb-3 text-blue-400">💡 Insights</h3>
          <ul className="space-y-2 text-sm text-gray-300">
            {overallStats.winrate >= 60 && (
              <li>✓ Excelente performance geral! Winrate acima de 60%</li>
            )}
            {confidenceStats[0] && confidenceStats[0].winrate > overallStats.winrate && (
              <li>✓ Sinais com maior confiança têm melhor performance</li>
            )}
            {overallStats.total < 30 && (
              <li>⚠ Aguarde mais sinais para estatísticas mais precisas (mín. 30)</li>
            )}
            {overallStats.total >= 100 && (
              <li>✓ Base de dados robusta com {overallStats.total}+ sinais</li>
            )}
          </ul>
        </div>
      )}
    </div>
  )
}

