import type { AppProps } from 'next/app'
import React, { useState, useEffect, ErrorInfo, ReactNode } from 'react'

// Error boundary component
class ErrorBoundary extends React.Component<{ children: ReactNode }, { hasError: boolean, error: Error | null }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: '20px', 
          textAlign: 'center',
          backgroundColor: '#ffebee',
          color: '#d32f2f',
          fontFamily: 'Arial, sans-serif'
        }}>
          <h2>Something went wrong</h2>
          <p>Please refresh the page and try again.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default function App({ Component, pageProps }: AppProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <ErrorBoundary>
      <style jsx global>{`
        * {
          box-sizing: border-box;
        }
        
        body {
          margin: 0;
          font-family: 'Segoe UI', Roboto, Arial, sans-serif;
          background-color: #f5f5f5;
          color: #333;
        }
        
        h1, h2, h3, h4, h5, h6 {
          margin: 0;
          font-weight: 600;
        }
        
        button {
          font-family: inherit;
        }
        
        input, textarea {
          font-family: inherit;
        }
      `}</style>
      <Component {...pageProps} />
    </ErrorBoundary>
  )
}