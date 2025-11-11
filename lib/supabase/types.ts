export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      signals: {
        Row: {
          id: string
          created_at: string
          timestamp: string
          symbol: string
          timeframe: string
          prediction: 'CALL' | 'PUT'
          confidence_score: number
          open_price: number
          close_price: number | null
          result: 'WIN' | 'LOSS' | 'PENDING' | null
          features: Json
        }
        Insert: {
          id?: string
          created_at?: string
          timestamp: string
          symbol: string
          timeframe: string
          prediction: 'CALL' | 'PUT'
          confidence_score: number
          open_price: number
          close_price?: number | null
          result?: 'WIN' | 'LOSS' | 'PENDING' | null
          features?: Json
        }
        Update: {
          id?: string
          created_at?: string
          timestamp?: string
          symbol?: string
          timeframe?: string
          prediction?: 'CALL' | 'PUT'
          confidence_score?: number
          open_price?: number
          close_price?: number | null
          result?: 'WIN' | 'LOSS' | 'PENDING' | null
          features?: Json
        }
      }
      performance_stats: {
        Row: {
          id: string
          created_at: string
          period: string
          total_signals: number
          wins: number
          losses: number
          winrate: number
          confidence_range: string
          avg_confidence: number
        }
        Insert: {
          id?: string
          created_at?: string
          period: string
          total_signals: number
          wins: number
          losses: number
          winrate: number
          confidence_range: string
          avg_confidence: number
        }
        Update: {
          id?: string
          created_at?: string
          period?: string
          total_signals?: number
          wins?: number
          losses?: number
          winrate?: number
          confidence_range?: string
          avg_confidence?: number
        }
      }
      user_settings: {
        Row: {
          id: string
          user_id: string
          min_confidence_threshold: number
          notification_enabled: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          min_confidence_threshold?: number
          notification_enabled?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          min_confidence_threshold?: number
          notification_enabled?: boolean
          created_at?: string
          updated_at?: string
        }
      }
      market_data: {
        Row: {
          id: string
          timestamp: string
          symbol: string
          timeframe: string
          open: number
          high: number
          low: number
          close: number
          volume: number
          created_at: string
        }
        Insert: {
          id?: string
          timestamp: string
          symbol: string
          timeframe: string
          open: number
          high: number
          low: number
          close: number
          volume: number
          created_at?: string
        }
        Update: {
          id?: string
          timestamp?: string
          symbol?: string
          timeframe?: string
          open?: number
          high?: number
          low?: number
          close?: number
          volume?: number
          created_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}

