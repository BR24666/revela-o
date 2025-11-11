'use client'

import { useState } from 'react'
import SignalsScreen from '@/components/SignalsScreen'
import PerformanceScreen from '@/components/PerformanceScreen'
import SettingsScreen from '@/components/SettingsScreen'
import Navigation from '@/components/Navigation'

type Screen = 'signals' | 'performance' | 'settings'

export default function Home() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('signals')

  return (
    <main className="min-h-screen bg-background">
      <header className="bg-card-bg border-b border-[var(--border)] py-4 px-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-center bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
            🤖 Super Analista BTC/USDT
          </h1>
          <p className="text-center text-sm text-gray-400 mt-1">
            Sistema de Previsão com IA - M1
          </p>
        </div>
      </header>

      <Navigation currentScreen={currentScreen} onScreenChange={setCurrentScreen} />

      <div className="max-w-7xl mx-auto px-4 py-6">
        {currentScreen === 'signals' && <SignalsScreen />}
        {currentScreen === 'performance' && <PerformanceScreen />}
        {currentScreen === 'settings' && <SettingsScreen />}
      </div>
    </main>
  )
}

