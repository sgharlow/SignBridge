import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton,
  Collapse,
} from '@mui/material'
import {
  Speed,
  TrendingUp,
  Memory,
  NetworkCheck,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material'

interface PerformanceMetrics {
  averageLatency: number
  successRate: number
  cacheHitRate: number
  requestCount: number
  errorCount: number
  lastUpdated: string
}

interface ProcessingHistory {
  timestamp: string
  latency: number
  success: boolean
  cacheHit: boolean
  translation: string
}

interface PerformanceMonitorProps {
  isActive: boolean
  processingHistory: ProcessingHistory[]
  currentMetrics?: PerformanceMetrics | null
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  isActive,
  processingHistory,
  currentMetrics
}) => {
  const [expanded, setExpanded] = useState(false)
  const [realtimeMetrics, setRealtimeMetrics] = useState<PerformanceMetrics | null>(null)

  // Calculate metrics from processing history
  useEffect(() => {
    if (processingHistory.length > 0) {
      const recent = processingHistory.slice(0, 10) // Last 10 requests
      const successful = recent.filter(h => h.success)
      const cached = recent.filter(h => h.cacheHit)
      
      const avgLatency = successful.length > 0 
        ? successful.reduce((sum, h) => sum + h.latency, 0) / successful.length
        : 0

      setRealtimeMetrics({
        averageLatency: avgLatency,
        successRate: (successful.length / recent.length) * 100,
        cacheHitRate: (cached.length / recent.length) * 100,
        requestCount: recent.length,
        errorCount: recent.length - successful.length,
        lastUpdated: new Date().toISOString()
      })
    }
  }, [processingHistory])

  const metrics = currentMetrics || realtimeMetrics

  const getLatencyColor = (latency: number) => {
    if (latency < 1) return 'success'
    if (latency < 2) return 'warning' 
    return 'error'
  }

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 95) return 'success'
    if (rate >= 80) return 'warning'
    return 'error'
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6">
            <Speed sx={{ mr: 1 }} />
            Performance Monitor
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Chip 
              label={isActive ? "ACTIVE" : "INACTIVE"} 
              color={isActive ? "success" : "default"}
              size="small"
            />
            <IconButton 
              size="small" 
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
        </Box>

        {/* Key Metrics */}
        {metrics && (
          <Grid container spacing={2} mb={2}>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color={getLatencyColor(metrics.averageLatency)}>
                  {metrics.averageLatency.toFixed(2)}s
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Avg Latency
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color={getSuccessRateColor(metrics.successRate)}>
                  {metrics.successRate.toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Success Rate
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary">
                  {metrics.cacheHitRate.toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Cache Hit Rate
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4">
                  {metrics.requestCount}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Requests
                </Typography>
              </Box>
            </Grid>
          </Grid>
        )}

        {/* Status Indicators */}
        <Box mb={2}>
          <Box display="flex" alignItems="center" gap={2} mb={1}>
            <NetworkCheck color={isActive ? "success" : "disabled"} />
            <Typography variant="body2">
              Pipeline Status: {isActive ? "Processing" : "Idle"}
            </Typography>
          </Box>
          
          {metrics && metrics.averageLatency > 0 && (
            <Box>
              <Typography variant="caption" color="text.secondary">
                Average Response Time
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((3 - metrics.averageLatency) / 3 * 100, 100)}
                color={getLatencyColor(metrics.averageLatency)}
                sx={{ height: 6, borderRadius: 3 }}
              />
            </Box>
          )}
        </Box>

        {/* Alerts */}
        {metrics && (
          <Box mb={2}>
            {metrics.successRate < 80 && (
              <Alert severity="warning">
                Low success rate detected. Check network connectivity.
              </Alert>
            )}
            {metrics.averageLatency > 3 && (
              <Alert severity="error">
                High latency detected. Consider optimizing frame size.
              </Alert>
            )}
            {metrics.cacheHitRate > 50 && (
              <Alert severity="info">
                Good cache performance - identical frames are being optimized.
              </Alert>
            )}
          </Box>
        )}

        {/* Detailed History */}
        <Collapse in={expanded}>
          <Typography variant="subtitle2" gutterBottom>
            Recent Processing History
          </Typography>
          {processingHistory.length > 0 ? (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Time</TableCell>
                  <TableCell>Latency</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Cache</TableCell>
                  <TableCell>Result</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {processingHistory.slice(0, 5).map((item, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Typography variant="caption">
                        {new Date(item.timestamp).toLocaleTimeString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={`${item.latency.toFixed(2)}s`}
                        size="small"
                        color={getLatencyColor(item.latency)}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={item.success ? "OK" : "ERR"}
                        size="small"
                        color={item.success ? "success" : "error"}
                      />
                    </TableCell>
                    <TableCell>
                      {item.cacheHit ? (
                        <Memory color="primary" fontSize="small" />
                      ) : (
                        <Memory color="disabled" fontSize="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" noWrap>
                        {item.translation.substring(0, 20)}
                        {item.translation.length > 20 ? '...' : ''}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No processing history yet
            </Typography>
          )}
        </Collapse>

        {/* Footer Info */}
        {metrics && (
          <Box mt={2} pt={1} borderTop="1px solid #eee">
            <Typography variant="caption" color="text.secondary">
              Last updated: {new Date(metrics.lastUpdated).toLocaleTimeString()}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default PerformanceMonitor