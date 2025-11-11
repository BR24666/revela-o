'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase/client'
import { TrendingUp, TrendingDown, Clock, Activity } from 'lucide-react'

interface Signal {
  id: string
  timestamp: string
  prediction: 'CALL' | 'PUT'
  confidence_score: number
  open_price: number
  close_price: number | null
  result: 'WIN' | 'LOSS' | 'PENDING' | null
}

export default function SignalsScreen() {
  const [latestSignal, setLatestSignal] = useState<Signal | null>(null)
  const [recentSignals, setRecentSignals] = useState<Signal[]>([])
  const [loading, setLoading] = useState(true)
  const [minConfidence, setMinConfidence] = useState(75)

  useEffect(() => {
    loadSignals()
    
    // Inscrever em novos sinais em tempo real
    const subscription = supabase
      .channel('signals_channel')
      .on('postgres_changes', 
        { event: 'INSERT', schema: 'public', table: 'signals' },
        (payload) => {
          console.log('Novo sinal recebido:', payload.new)
          const newSignal = payload.new as Signal
          
          // Atualizar apenas se confiança >= threshold
          if (newSignal.confidence_score >= minConfidence) {
            setLatestSignal(newSignal)
            setRecentSignals(prev => [newSignal, ...prev.slice(0, 9)])
          }
        }
      )
      .on('postgres_changes',
        { event: 'UPDATE', schema: 'public', table: 'signals' },
        (payload) => {
          console.log('Sinal atualizado:', payload.new)
          const updatedSignal = payload.new as Signal
          
          // Atualizar na lista
          setRecentSignals(prev => 
            prev.map(s => s.id === updatedSignal.id ? updatedSignal : s)
          )
          
          // Atualizar latest se for o mesmo
          if (latestSignal?.id === updatedSignal.id) {
            setLatestSignal(updatedSignal)
          }
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [minConfidence, latestSignal?.id])

  async function loadSignals() {
    try {
      setLoading(true)
      
      // Buscar sinais recentes (últimas 24h)
      const { data, error } = await supabase
        .from('signals')
        .select('*')
        .gte('confidence_score', minConfidence)
        .order('timestamp', { ascending: false })
        .limit(10)

      if (error) throw error

      if (data && data.length > 0) {
        setLatestSignal(data[0])
        setRecentSignals(data)
      }
    } catch (error) {
      console.error('Erro ao carregar sinais:', error)
    } finally {
      setLoading(false)
    }
  }

  function formatTime(timestamp: string) {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  function formatDate(timestamp: string) {
    return new Date(timestamp).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Activity className="animate-spin mx-auto mb-4" size={48} />
          <p className="text-gray-400">Carregando sinais...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Sinal Principal */}
      <div className="card">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-6 flex items-center justify-center gap-2">
            <Activity className="text-blue-500" />
            Sinal Atual
          </h2>

          {latestSignal ? (
            <div className="space-y-4">
              {/* Direção */}
              <div className={`
                py-12 px-8 rounded-xl border-4 
                ${latestSignal.prediction === 'CALL' 
                  ? 'bg-green-500/10 border-green-500' 
                  : 'bg-red-500/10 border-red-500'
                }
              `}>
                {latestSignal.prediction === 'CALL' ? (
                  <TrendingUp size={64} className="text-green-500 mx-auto mb-4" />
                ) : (
                  <TrendingDown size={64} className="text-red-500 mx-auto mb-4" />
                )}
                
                <h3 className={`text-5xl font-bold mb-2 ${
                  latestSignal.prediction === 'CALL' ? 'text-green-500' : 'text-red-500'
                }`}>
                  {latestSignal.prediction}
                </h3>
                
                <p className="text-gray-400 text-sm mb-4">
                  {latestSignal.prediction === 'CALL' ? 'Compra (Verde)' : 'Venda (Vermelha)'}
                </p>

                <div className="flex items-center justify-center gap-6 text-sm">
                  <div>
                    <p className="text-gray-400">Confiança</p>
                    <p className="text-2xl font-bold">{latestSignal.confidence_score.toFixed(2)}%</p>
                  </div>
                  <div className="h-12 w-px bg-gray-700"></div>
                  <div>
                    <p className="text-gray-400">Preço</p>
                    <p className="text-2xl font-bold">${latestSignal.open_price.toFixed(2)}</p>
                  </div>
                </div>
              </div>

              {/* Resultado (se disponível) */}
              {latestSignal.result && latestSignal.result !== 'PENDING' && (
                <div className={`
                  py-4 px-6 rounded-lg
                  ${latestSignal.result === 'WIN' 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-red-500/20 text-red-400'
                  }
                `}>
                  <p className="font-bold text-lg">
                    {latestSignal.result === 'WIN' ? '✅ ACERTOU!' : '❌ ERROU'}
                  </p>
                  {latestSignal.close_price && (
                    <p className="text-sm mt-1">
                      Fechamento: ${latestSignal.close_price.toFixed(2)}
                    </p>
                  )}
                </div>
              )}

              {/* Info */}
              <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
                <Clock size={16} />
                <span>{formatTime(latestSignal.timestamp)}</span>
                <span>•</span>
                <span>{formatDate(latestSignal.timestamp)}</span>
              </div>
            </div>
          ) : (
            <div className="py-16">
              <Clock size={48} className="mx-auto mb-4 text-gray-600" />
              <p className="text-gray-400 text-lg">Aguardando próximo sinal...</p>
              <p className="text-gray-500 text-sm mt-2">
                Mín. confiança: {minConfidence}%
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Histórico Recente */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Últimos Sinais</h3>
        
        {recentSignals.length > 0 ? (
          <div className="space-y-2">
            {recentSignals.map((signal) => (
              <div 
                key={signal.id}
                className={`
                  flex items-center justify-between p-4 rounded-lg border
                  ${signal.prediction === 'CALL' 
                    ? 'bg-green-500/5 border-green-500/30' 
                    : 'bg-red-500/5 border-red-500/30'
                  }
                `}
              >
                <div className="flex items-center gap-4">
                  {signal.prediction === 'CALL' ? (
                    <TrendingUp className="text-green-500" size={24} />
                  ) : (
                    <TrendingDown className="text-red-500" size={24} />
                  )}
                  
                  <div>
                    <p className="font-semibold">{signal.prediction}</p>
                    <p className="text-sm text-gray-400">{formatTime(signal.timestamp)}</p>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <p className="text-sm text-gray-400">Confiança</p>
                    <p className="font-semibold">{signal.confidence_score.toFixed(1)}%</p>
                  </div>

                  {signal.result && signal.result !== 'PENDING' && (
                    <div className={`
                      px-3 py-1 rounded-full text-sm font-bold
                      ${signal.result === 'WIN' 
                        ? 'bg-green-500 text-white' 
                        : 'bg-red-500 text-white'
                      }
                    `}>
                      {signal.result}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-gray-500 py-8">
            Nenhum sinal ainda
          </p>
        )}
      </div>
    </div>
  )
}

