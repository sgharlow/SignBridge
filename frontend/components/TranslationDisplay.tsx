import React from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  Chip,
  LinearProgress,
} from '@mui/material'
import { VolumeUp, AccessTime } from '@mui/icons-material'

interface TranslationResult {
  translation: string
  confidence: number
  timestamp: string
  device_id: string
}

interface TranslationDisplayProps {
  result: TranslationResult | null
  isProcessing: boolean
  onSpeak: (text: string) => void
}

export const TranslationDisplay: React.FC<TranslationDisplayProps> = ({
  result,
  isProcessing,
  onSpeak
}) => {
  const getConfidenceColor = (confidence: number) => {
    if (confidence > 0.7) return 'success'
    if (confidence > 0.4) return 'warning'
    return 'error'
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence > 0.7) return 'High Confidence'
    if (confidence > 0.4) return 'Medium Confidence'
    return 'Low Confidence'
  }

  if (isProcessing) {
    return (
      <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="primary" gutterBottom>
          Processing sign language...
        </Typography>
        <LinearProgress sx={{ mt: 2 }} />
      </Paper>
    )
  }

  if (!result) {
    return (
      <Paper elevation={1} sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          Start video capture to see translations appear here
        </Typography>
      </Paper>
    )
  }

  return (
    <Paper
      elevation={3}
      sx={{
        p: 3,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        borderRadius: 2
      }}
    >
      {/* Main Translation */}
      <Typography variant="h4" gutterBottom fontWeight="bold">
        "{result.translation}"
      </Typography>

      {/* Confidence Indicator */}
      <Box display="flex" alignItems="center" gap={2} mb={2}>
        <Chip
          label={getConfidenceLabel(result.confidence)}
          color={getConfidenceColor(result.confidence)}
          size="small"
        />
        <Typography variant="body2">
          {(result.confidence * 100).toFixed(1)}% confidence
        </Typography>
      </Box>

      {/* Timestamp */}
      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <AccessTime fontSize="small" />
        <Typography variant="caption">
          {new Date(result.timestamp).toLocaleTimeString()}
        </Typography>
      </Box>

      {/* Actions */}
      <Box display="flex" gap={2}>
        <Button
          variant="contained"
          startIcon={<VolumeUp />}
          onClick={() => onSpeak(result.translation)}
          sx={{
            backgroundColor: 'rgba(255,255,255,0.2)',
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.3)',
            }
          }}
        >
          Speak
        </Button>
      </Box>
    </Paper>
  )
}