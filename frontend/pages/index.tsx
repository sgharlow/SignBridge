import { useState, useRef, useEffect, useCallback } from 'react'
import Head from 'next/head'

// API Configuration
const API_ENDPOINT = process.env.NEXT_PUBLIC_API_ENDPOINT || 'https://your-api-gateway-endpoint.amazonaws.com/prod/process'

interface TranslationResult {
  translation: string
  confidence: number
  timestamp: string
  device_id: string
}

// Create ASL Hello image (same as our successful test)
const createASLHelloImage = (): string => {
  const canvas = document.createElement('canvas')
  canvas.width = 640
  canvas.height = 480
  const ctx = canvas.getContext('2d')
  
  if (!ctx) {
    throw new Error('Canvas context not available')
  }
  
  // Create white background
  ctx.fillStyle = 'white'
  ctx.fillRect(0, 0, 640, 480)
  
  // Draw hand outline for "Hello" sign (open palm)
  const handCoords = [
    [200, 200], [250, 180], [300, 190], [350, 200], [400, 220],  // fingers
    [420, 250], [400, 300], [350, 350], [300, 380], [250, 390],  // palm
    [200, 380], [150, 350], [120, 300], [140, 250], [170, 220]   // thumb
  ]
  
  ctx.fillStyle = '#FFD2A5'
  ctx.strokeStyle = 'black'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(handCoords[0][0], handCoords[0][1])
  
  for (let i = 1; i < handCoords.length; i++) {
    ctx.lineTo(handCoords[i][0], handCoords[i][1])
  }
  ctx.closePath()
  ctx.fill()
  ctx.stroke()
  
  // Add text labels
  ctx.fillStyle = 'black'
  ctx.font = '20px Arial'
  ctx.fillText('ASL: Hello Sign', 50, 50)
  ctx.fillText('Open palm gesture', 50, 450)
  
  // Convert to base64 (same format as our test)
  const dataURL = canvas.toDataURL('image/jpeg', 0.85)
  return dataURL.split(',')[1]
}

export default function Home() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const [isVideoActive, setIsVideoActive] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [lastResult, setLastResult] = useState<TranslationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [processingCount, setProcessingCount] = useState(0)

  // Start video capture
  const startVideo = useCallback(async () => {
    try {
      setError(null)
      console.log('Starting camera...')
      
      // Check if mediaDevices is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera access not supported in this browser')
      }

      console.log('Requesting camera access...')
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640, min: 320 },
          height: { ideal: 480, min: 240 },
          facingMode: 'user'
        },
        audio: false
      })
      
      console.log('Camera stream obtained:', stream)
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        
        // Wait for video to load
        videoRef.current.onloadedmetadata = () => {
          console.log('Video metadata loaded, starting playback')
          videoRef.current?.play().then(() => {
            console.log('Video playing, setting active state')
            setIsVideoActive(true)
            
            // Start processing frames every 3 seconds (increased interval)
            console.log('Starting frame processing interval')
            intervalRef.current = setInterval(() => {
              console.log('Processing frame...')
              captureAndProcess()
            }, 3000)
          }).catch(err => {
            console.error('Error playing video:', err)
            setError('Failed to start video playback: ' + err.message)
          })
        }
        
        videoRef.current.onerror = (err) => {
          console.error('Video error:', err)
          setError('Video playback error occurred')
        }
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      let errorMessage = 'Could not access camera. '
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMessage += 'Please allow camera permissions and try again.'
        } else if (error.name === 'NotFoundError') {
          errorMessage += 'No camera found. Please connect a camera and try again.'
        } else if (error.name === 'NotSupportedError') {
          errorMessage += 'Camera not supported in this browser.'
        } else {
          errorMessage += error.message
        }
      } else {
        errorMessage += 'Unknown error occurred.'
      }
      
      setError(errorMessage)
    }
  }, [])

  // Stop video capture
  const stopVideo = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    
    setIsVideoActive(false)
    setIsProcessing(false)
  }, [])

  // Capture frame and process with API
  const captureAndProcess = useCallback(async () => {
    console.log('captureAndProcess called')
    
    if (!videoRef.current || !canvasRef.current) {
      console.log('Video or canvas ref not available')
      setError('Video elements not initialized')
      return
    }

    if (isProcessing) {
      console.log('Already processing, skipping frame')
      return
    }

    const video = videoRef.current
    const canvas = canvasRef.current
    const context = canvas.getContext('2d')

    if (!context) {
      console.log('Canvas context not available')
      setError('Canvas not supported')
      return
    }

    // Check if video is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.log('Video not ready, readyState:', video.readyState)
      setError('Video not ready for capture')
      return
    }

    // Check if video dimensions are available
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      console.log('Video dimensions not available:', video.videoWidth, 'x', video.videoHeight)
      setError('Video dimensions not available')
      return
    }

    try {
      console.log('Capturing frame from video:', video.videoWidth, 'x', video.videoHeight)
      
      // Set canvas size to match video
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight

      // Draw current video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height)

      // Convert to base64
      const dataURL = canvas.toDataURL('image/jpeg', 0.8)
      const frameData = dataURL.split(',')[1]

      // Check if we actually got frame data
      if (!frameData || frameData.length < 100) {
        console.log('No valid frame data captured, length:', frameData?.length)
        console.log('Full dataURL:', dataURL?.substring(0, 100) + '...')
        setError('Failed to capture frame data')
        return
      }

      console.log('Frame captured, size:', frameData.length, 'bytes')
      console.log('Frame data format:', dataURL.substring(0, 50))
      console.log('Frame data sample:', frameData.substring(0, 100) + '...')
      
      // Validate base64
      try {
        atob(frameData)
        console.log('✅ Valid base64 format')
      } catch (e) {
        console.log('❌ Invalid base64 format:', e)
        setError('Invalid frame data format')
        return
      }
      setIsProcessing(true)
      setProcessingCount(prev => prev + 1)

      console.log('Sending to API:', API_ENDPOINT)
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          frame_data: frameData,
          timestamp: new Date().toISOString(),
          device_id: 'web-interface'
        })
      })

      console.log('API response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.log('API error response:', errorText)
        throw new Error(`API Error: ${response.status} - ${errorText}`)
      }

      const result: TranslationResult = await response.json()
      console.log('API result:', result)
      
      setIsProcessing(false)
      setLastResult(result)
      setError(null)

      // Text-to-speech for accessibility
      if (result.confidence > 0.5 && result.translation && result.translation !== 'No clear signs detected') {
        speak(result.translation)
      }

    } catch (error) {
      console.error('Processing error:', error)
      setIsProcessing(false)
      setError(`Processing failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }, [isProcessing])

  // Text-to-speech function
  const speak = useCallback((text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.8
      utterance.pitch = 1
      utterance.volume = 0.8
      speechSynthesis.speak(utterance)
    }
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopVideo()
    }
  }, [stopVideo])

  return (
    <>
      <Head>
        <title>SignBridge - Real-time Sign Language Interpreter</title>
        <meta name="description" content="AI-powered sign language interpretation using AWS Bedrock" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '10px' }}>
            🌉 SignBridge
          </h1>
          <h2 style={{ fontSize: '1.2rem', color: '#666', marginBottom: '10px' }}>
            Real-time Sign Language Interpreter powered by AWS Bedrock
          </h2>
          <div style={{ 
            display: 'inline-block', 
            backgroundColor: '#1976d2', 
            color: 'white', 
            padding: '5px 15px', 
            borderRadius: '20px',
            fontSize: '0.9rem'
          }}>
            AWS Breaking Barriers Hackathon 2025
          </div>
        </div>

        <div style={{ display: 'flex', gap: '30px', flexWrap: 'wrap' }}>
          {/* Video Feed */}
          <div style={{ flex: '2', minWidth: '400px' }}>
            <div style={{ 
              border: '1px solid #ddd', 
              borderRadius: '8px', 
              padding: '20px',
              backgroundColor: 'white'
            }}>
              <h3 style={{ marginBottom: '20px' }}>Video Feed</h3>
              
              <div style={{ position: 'relative', marginBottom: '20px' }}>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  style={{
                    width: '100%',
                    maxWidth: '640px',
                    height: 'auto',
                    backgroundColor: '#000',
                    borderRadius: '8px'
                  }}
                />
                <canvas
                  ref={canvasRef}
                  style={{ display: 'none' }}
                />
                
                {/* Processing Overlay */}
                {isProcessing && (
                  <div style={{
                    position: 'absolute',
                    top: '16px',
                    right: '16px',
                    backgroundColor: 'rgba(0,0,0,0.7)',
                    color: 'white',
                    padding: '8px',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}>
                    🔄 Processing...
                  </div>
                )}
                
                {/* Frame Counter */}
                {isVideoActive && (
                  <div style={{
                    position: 'absolute',
                    bottom: '16px',
                    left: '16px',
                    backgroundColor: 'rgba(0,0,0,0.7)',
                    color: 'white',
                    padding: '8px',
                    borderRadius: '4px',
                    fontSize: '12px'
                  }}>
                    Frames processed: {processingCount}
                  </div>
                )}
              </div>

              {/* Controls */}
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                {!isVideoActive ? (
                  <>
                    <button
                      style={{
                        padding: '12px 24px',
                        fontSize: '16px',
                        backgroundColor: '#1976d2',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                      onClick={startVideo}
                    >
                      📹 Start Camera
                    </button>
                    <button
                      style={{
                        padding: '8px 16px',
                        fontSize: '14px',
                        backgroundColor: '#666',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        marginLeft: '10px'
                      }}
                      onClick={async () => {
                        try {
                          const devices = await navigator.mediaDevices.enumerateDevices()
                          const videoDevices = devices.filter(device => device.kind === 'videoinput')
                          alert(`Found ${videoDevices.length} camera(s):\n${videoDevices.map(d => d.label || 'Camera').join('\n')}`)
                        } catch (e) {
                          alert('Cannot enumerate cameras: ' + (e instanceof Error ? e.message : 'Unknown error'))
                        }
                      }}
                    >
                      🔍 Check Cameras
                    </button>
                    <button
                      style={{
                        padding: '8px 16px',
                        fontSize: '14px',
                        backgroundColor: '#9c27b0',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        marginLeft: '10px'
                      }}
                      onClick={async () => {
                        try {
                          // Use the same ASL "Hello" image that worked in our test
                          const aslHelloImage = createASLHelloImage()
                          console.log('ASL Hello test image size:', aslHelloImage.length)
                          
                          const response = await fetch(API_ENDPOINT, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                              frame_data: aslHelloImage,
                              timestamp: new Date().toISOString(),
                              device_id: 'asl-hello-test'
                            })
                          })
                          
                          console.log('ASL test response status:', response.status)
                          const result = await response.json()
                          console.log('ASL test result:', result)
                          setLastResult(result)
                          
                          if (result.translation === 'HELLO' || result.translation?.includes('HELLO')) {
                            console.log('✅ Frontend-to-API communication is working!')
                          } else {
                            console.log('⚠️ Expected HELLO but got:', result.translation)
                          }
                        } catch (e) {
                          console.error('ASL test error:', e)
                          setError('ASL test failed: ' + (e instanceof Error ? e.message : 'Unknown error'))
                        }
                      }}
                    >
                      🧪 Test ASL
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      style={{
                        padding: '12px 24px',
                        fontSize: '16px',
                        backgroundColor: '#d32f2f',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                      onClick={stopVideo}
                    >
                      ⏹️ Stop Camera
                    </button>
                    <button
                      style={{
                        padding: '8px 16px',
                        fontSize: '14px',
                        backgroundColor: '#ff9800',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        marginLeft: '10px'
                      }}
                      onClick={() => {
                        console.log('Manual capture triggered')
                        captureAndProcess()
                      }}
                      disabled={isProcessing}
                    >
                      📸 Test Capture
                    </button>
                  </>
                )}
              </div>

              {/* Error Display */}
              {error && (
                <div style={{
                  marginTop: '15px',
                  padding: '12px',
                  backgroundColor: '#ffebee',
                  border: '1px solid #f44336',
                  borderRadius: '4px',
                  color: '#d32f2f'
                }}>
                  ⚠️ {error}
                </div>
              )}
            </div>
          </div>

          {/* Translation Results */}
          <div style={{ flex: '1', minWidth: '300px' }}>
            <div style={{ 
              border: '1px solid #ddd', 
              borderRadius: '8px', 
              padding: '20px',
              backgroundColor: 'white'
            }}>
              <h3 style={{ marginBottom: '20px' }}>🔮 Live Translation</h3>

              {/* Current Result */}
              {lastResult ? (
                <div style={{
                  padding: '15px',
                  marginBottom: '15px',
                  backgroundColor: '#1976d2',
                  color: 'white',
                  borderRadius: '8px'
                }}>
                  <h4 style={{ marginBottom: '10px', fontSize: '1.2rem' }}>
                    {lastResult.translation}
                  </h4>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <small>
                      Confidence: {(lastResult.confidence * 100).toFixed(1)}%
                    </small>
                    <button
                      style={{
                        backgroundColor: 'transparent',
                        border: '1px solid white',
                        color: 'white',
                        padding: '5px 10px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                      onClick={() => speak(lastResult.translation)}
                    >
                      🔊 Speak
                    </button>
                  </div>
                </div>
              ) : (
                <div style={{
                  padding: '15px',
                  marginBottom: '15px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '8px',
                  color: '#666'
                }}>
                  {isVideoActive ? 'Waiting for sign language input...' : 'Start camera to begin translation'}
                </div>
              )}

              {/* Instructions */}
              <div style={{ marginTop: '20px' }}>
                <h4 style={{ marginBottom: '15px' }}>How to Use</h4>
                <ol style={{ fontSize: '14px', lineHeight: '1.6' }}>
                  <li>Click "Start Camera" to begin</li>
                  <li>Position yourself clearly in the camera view</li>
                  <li>Perform ASL signs slowly and clearly</li>
                  <li>Translations appear in real-time</li>
                  <li>Click "Speak" to hear the translation</li>
                </ol>
              </div>

              {/* Status */}
              <div style={{ 
                marginTop: '20px', 
                padding: '10px', 
                backgroundColor: isVideoActive ? '#e8f5e8' : '#fff3e0',
                borderRadius: '4px',
                fontSize: '14px'
              }}>
                Status: {isVideoActive ? '🟢 Active' : '🟡 Inactive'}
                <br />
                API: {API_ENDPOINT ? '🟢 Connected' : '🔴 Not configured'}
                {isVideoActive && videoRef.current && (
                  <>
                    <br />
                    Video: {videoRef.current.videoWidth}x{videoRef.current.videoHeight}
                    <br />
                    Ready: {videoRef.current.readyState === 4 ? '🟢 Yes' : '🟡 Loading'}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ 
          textAlign: 'center', 
          marginTop: '30px', 
          paddingTop: '20px', 
          borderTop: '1px solid #eee',
          color: '#666',
          fontSize: '14px'
        }}>
          SignBridge • Powered by AWS Bedrock • Built for AWS Breaking Barriers Hackathon 2025
        </div>
      </div>
    </>
  )
}