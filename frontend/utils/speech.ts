export class TextToSpeechService {
  private static instance: TextToSpeechService
  private isSupported: boolean
  private currentUtterance: SpeechSynthesisUtterance | null = null

  constructor() {
    this.isSupported = 'speechSynthesis' in window
  }

  static getInstance(): TextToSpeechService {
    if (!TextToSpeechService.instance) {
      TextToSpeechService.instance = new TextToSpeechService()
    }
    return TextToSpeechService.instance
  }

  speak(text: string, options: {
    rate?: number
    pitch?: number
    volume?: number
    voice?: SpeechSynthesisVoice
  } = {}): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.isSupported) {
        reject(new Error('Text-to-speech is not supported in this browser'))
        return
      }

      // Stop any currently playing speech
      this.stop()

      const utterance = new SpeechSynthesisUtterance(text)
      
      // Set voice options
      utterance.rate = options.rate ?? 0.8
      utterance.pitch = options.pitch ?? 1.0
      utterance.volume = options.volume ?? 0.8
      
      if (options.voice) {
        utterance.voice = options.voice
      }

      // Event handlers
      utterance.onend = () => {
        this.currentUtterance = null
        resolve()
      }

      utterance.onerror = (event) => {
        this.currentUtterance = null
        reject(new Error(`Speech synthesis error: ${event.error}`))
      }

      this.currentUtterance = utterance
      speechSynthesis.speak(utterance)
    })
  }

  stop(): void {
    if (this.isSupported && speechSynthesis.speaking) {
      speechSynthesis.cancel()
      this.currentUtterance = null
    }
  }

  pause(): void {
    if (this.isSupported && speechSynthesis.speaking) {
      speechSynthesis.pause()
    }
  }

  resume(): void {
    if (this.isSupported && speechSynthesis.paused) {
      speechSynthesis.resume()
    }
  }

  getVoices(): SpeechSynthesisVoice[] {
    if (!this.isSupported) return []
    return speechSynthesis.getVoices()
  }

  isPlaying(): boolean {
    return this.isSupported && speechSynthesis.speaking
  }

  isPaused(): boolean {
    return this.isSupported && speechSynthesis.paused
  }

  getDefaultVoice(): SpeechSynthesisVoice | null {
    const voices = this.getVoices()
    
    // Prefer English voices
    const englishVoices = voices.filter(voice => 
      voice.lang.startsWith('en-') && voice.default
    )
    
    if (englishVoices.length > 0) {
      return englishVoices[0]
    }

    // Fallback to any English voice
    const anyEnglishVoice = voices.find(voice => voice.lang.startsWith('en-'))
    if (anyEnglishVoice) {
      return anyEnglishVoice
    }

    // Last resort: any voice
    return voices[0] || null
  }
}

export default TextToSpeechService.getInstance()