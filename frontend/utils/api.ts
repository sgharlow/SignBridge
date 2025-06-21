const API_ENDPOINT = process.env.NEXT_PUBLIC_API_ENDPOINT || 'https://your-api-gateway-endpoint.amazonaws.com/prod/process'

export interface TranslationRequest {
  frame_data: string
  timestamp: string
  device_id: string
}

export interface TranslationResponse {
  translation: string
  confidence: number
  timestamp: string
  device_id: string
}

export interface ApiError {
  error: string
  message?: string
}

export class SignToMeAPI {
  private static instance: SignToMeAPI
  private requestCount = 0

  static getInstance(): SignToMeAPI {
    if (!SignToMeAPI.instance) {
      SignToMeAPI.instance = new SignToMeAPI()
    }
    return SignToMeAPI.instance
  }

  async processFrame(request: TranslationRequest): Promise<TranslationResponse> {
    this.requestCount++
    
    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': `web-${Date.now()}-${this.requestCount}`,
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
          error: `HTTP ${response.status}: ${response.statusText}`
        }))
        throw new Error(errorData.error || `Request failed with status ${response.status}`)
      }

      const result: TranslationResponse = await response.json()
      
      // Validate response structure
      if (!result.translation || typeof result.confidence !== 'number') {
        throw new Error('Invalid response format from API')
      }

      return result
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error: Unable to connect to SignToMe API')
      }
      throw error
    }
  }

  getRequestCount(): number {
    return this.requestCount
  }

  resetRequestCount(): void {
    this.requestCount = 0
  }
}

export default SignToMeAPI.getInstance()