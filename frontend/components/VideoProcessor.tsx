import { useRef, useCallback, useEffect } from 'react'

interface VideoProcessorProps {
  videoRef: React.RefObject<HTMLVideoElement>
  onFrameCapture: (frameData: string) => void
  isActive: boolean
  intervalMs?: number
}

export const useVideoProcessor = ({
  videoRef,
  onFrameCapture,
  isActive,
  intervalMs = 2000
}: VideoProcessorProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const captureFrame = useCallback(() => {
    if (!videoRef.current) return

    const video = videoRef.current
    if (video.videoWidth === 0) return

    // Create canvas dynamically
    const canvas = document.createElement('canvas')
    const context = canvas.getContext('2d')
    if (!context) return

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Draw the current video frame
    context.drawImage(video, 0, 0, canvas.width, canvas.height)

    // Convert to base64 JPEG with quality optimization
    const frameData = canvas.toDataURL('image/jpeg', 0.8).split(',')[1]
    onFrameCapture(frameData)
  }, [videoRef, onFrameCapture])

  // Canvas is created dynamically in captureFrame if needed

  useEffect(() => {
    if (isActive) {
      intervalRef.current = setInterval(captureFrame, intervalMs)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isActive, captureFrame, intervalMs])

  return { canvasRef }
}