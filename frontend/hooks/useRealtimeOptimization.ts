import { useState, useCallback, useRef, useEffect } from 'react'

interface OptimizationMetrics {
  frameRate: number
  processingInterval: number
  qualityLevel: number
  adaptiveMode: boolean
  lastOptimization: string
}

interface PerformanceData {
  latency: number
  success: boolean
  timestamp: string
  cacheHit?: boolean
}

interface OptimizationSettings {
  targetLatency: number // Target latency in seconds
  maxFrameRate: number // Maximum frames per second
  minFrameRate: number // Minimum frames per second
  adaptiveQuality: boolean // Whether to adapt quality based on performance
}

const DEFAULT_SETTINGS: OptimizationSettings = {
  targetLatency: 1.5, // 1.5 seconds target
  maxFrameRate: 1, // 1 frame per second max
  minFrameRate: 0.2, // 1 frame per 5 seconds min
  adaptiveQuality: true
}

export const useRealtimeOptimization = (settings: Partial<OptimizationSettings> = {}) => {
  const config = { ...DEFAULT_SETTINGS, ...settings }
  
  const [metrics, setMetrics] = useState<OptimizationMetrics>({
    frameRate: 0.5, // Start with 1 frame per 2 seconds
    processingInterval: 2000, // 2 seconds
    qualityLevel: 0.8, // 80% JPEG quality
    adaptiveMode: true,
    lastOptimization: new Date().toISOString()
  })
  
  const performanceHistory = useRef<PerformanceData[]>([])
  const lastOptimizationTime = useRef<number>(Date.now())
  
  // Add performance data point
  const addPerformanceData = useCallback((data: PerformanceData) => {
    performanceHistory.current.unshift(data)
    
    // Keep only last 20 data points
    if (performanceHistory.current.length > 20) {
      performanceHistory.current = performanceHistory.current.slice(0, 20)
    }
    
    // Trigger optimization check after adding data
    optimizeSettings()
  }, [])
  
  // Calculate recent performance metrics
  const getRecentMetrics = useCallback(() => {
    const recent = performanceHistory.current.slice(0, 10) // Last 10 requests
    if (recent.length === 0) return null
    
    const successful = recent.filter(d => d.success)
    const avgLatency = successful.length > 0 
      ? successful.reduce((sum, d) => sum + d.latency, 0) / successful.length 
      : 0
    
    const successRate = successful.length / recent.length
    const cacheHitRate = recent.filter(d => d.cacheHit).length / recent.length
    
    return {
      avgLatency,
      successRate,
      cacheHitRate,
      sampleSize: recent.length
    }
  }, [])
  
  // Optimize settings based on performance
  const optimizeSettings = useCallback(() => {
    const now = Date.now()
    
    // Only optimize every 10 seconds to avoid thrashing
    if (now - lastOptimizationTime.current < 10000) {
      return
    }
    
    const recentMetrics = getRecentMetrics()
    if (!recentMetrics || recentMetrics.sampleSize < 3) {
      return // Need at least 3 data points
    }
    
    const { avgLatency, successRate } = recentMetrics
    
    let newFrameRate = metrics.frameRate
    let newQualityLevel = metrics.qualityLevel
    let optimizationMade = false
    
    // Adjust frame rate based on latency
    if (avgLatency > config.targetLatency * 1.2) {
      // Latency too high - reduce frame rate
      newFrameRate = Math.max(
        config.minFrameRate,
        metrics.frameRate * 0.8
      )
      optimizationMade = true
    } else if (avgLatency < config.targetLatency * 0.7 && successRate > 0.9) {
      // Latency good and success rate high - can increase frame rate
      newFrameRate = Math.min(
        config.maxFrameRate,
        metrics.frameRate * 1.2
      )
      optimizationMade = true
    }
    
    // Adjust quality based on performance (if adaptive quality enabled)
    if (config.adaptiveQuality) {
      if (avgLatency > config.targetLatency * 1.5) {
        // Very high latency - reduce quality
        newQualityLevel = Math.max(0.5, metrics.qualityLevel - 0.1)
        optimizationMade = true
      } else if (avgLatency < config.targetLatency * 0.5 && successRate > 0.95) {
        // Very good performance - can increase quality
        newQualityLevel = Math.min(0.9, metrics.qualityLevel + 0.05)
        optimizationMade = true
      }
    }
    
    // Apply optimizations if any were made
    if (optimizationMade) {
      setMetrics(prev => ({
        ...prev,
        frameRate: newFrameRate,
        processingInterval: Math.round(1000 / newFrameRate),
        qualityLevel: newQualityLevel,
        lastOptimization: new Date().toISOString()
      }))
      
      lastOptimizationTime.current = now
      
      console.log('🔧 Optimization applied:', {
        frameRate: newFrameRate,
        interval: Math.round(1000 / newFrameRate),
        quality: newQualityLevel,
        trigger: { avgLatency, successRate }
      })
    }
  }, [metrics, config, getRecentMetrics])
  
  // Manual optimization trigger
  const forceOptimization = useCallback(() => {
    lastOptimizationTime.current = 0 // Reset timer
    optimizeSettings()
  }, [optimizeSettings])
  
  // Reset to default settings
  const resetOptimization = useCallback(() => {
    setMetrics({
      frameRate: 0.5,
      processingInterval: 2000,
      qualityLevel: 0.8,
      adaptiveMode: true,
      lastOptimization: new Date().toISOString()
    })
    
    performanceHistory.current = []
    lastOptimizationTime.current = Date.now()
  }, [])
  
  // Get optimization recommendations
  const getRecommendations = useCallback(() => {
    const recentMetrics = getRecentMetrics()
    if (!recentMetrics) return []
    
    const recommendations = []
    const { avgLatency, successRate, cacheHitRate } = recentMetrics
    
    if (avgLatency > config.targetLatency * 1.5) {
      recommendations.push({
        type: 'warning',
        message: 'High latency detected. Consider reducing frame rate or image quality.',
        action: 'Reduce processing frequency'
      })
    }
    
    if (successRate < 0.8) {
      recommendations.push({
        type: 'error',
        message: 'Low success rate. Check network connectivity or API availability.',
        action: 'Check connection'
      })
    }
    
    if (cacheHitRate > 0.7) {
      recommendations.push({
        type: 'info',
        message: 'High cache hit rate. Good frame deduplication performance.',
        action: 'Optimal caching'
      })
    }
    
    if (avgLatency < config.targetLatency * 0.5 && successRate > 0.95) {
      recommendations.push({
        type: 'success',
        message: 'Excellent performance. Consider increasing frame rate for better responsiveness.',
        action: 'Increase frequency'
      })
    }
    
    return recommendations
  }, [getRecentMetrics, config])
  
  // Auto-optimization effect
  useEffect(() => {
    if (metrics.adaptiveMode) {
      const interval = setInterval(optimizeSettings, 15000) // Check every 15 seconds
      return () => clearInterval(interval)
    }
  }, [metrics.adaptiveMode, optimizeSettings])
  
  return {
    metrics,
    addPerformanceData,
    getRecentMetrics,
    forceOptimization,
    resetOptimization,
    getRecommendations,
    performanceHistory: performanceHistory.current
  }
}