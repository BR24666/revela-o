'use client'

import { TrendingUp, BarChart3, Settings } from 'lucide-react'

type Screen = 'signals' | 'performance' | 'settings'

interface NavigationProps {
  currentScreen: Screen
  onScreenChange: (screen: Screen) => void
}

export default function Navigation({ currentScreen, onScreenChange }: NavigationProps) {
  const navItems = [
    { id: 'signals' as Screen, label: 'Sinais', icon: TrendingUp },
    { id: 'performance' as Screen, label: 'Performance', icon: BarChart3 },
    { id: 'settings' as Screen, label: 'Configurações', icon: Settings },
  ]

  return (
    <nav className="bg-card-bg border-b border-[var(--border)]">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-center space-x-8">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => onScreenChange(id)}
              className={`
                flex items-center space-x-2 py-4 px-2 border-b-2 transition-colors
                ${currentScreen === id
                  ? 'border-blue-500 text-blue-500'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
                }
              `}
            >
              <Icon size={20} />
              <span className="font-medium">{label}</span>
            </button>
          ))}
        </div>
      </div>
    </nav>
  )
}

