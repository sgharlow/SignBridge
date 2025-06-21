import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta charSet="utf-8" />
        <meta name="theme-color" content="#1976d2" />
        <meta name="description" content="SignBridge - AI-powered real-time sign language interpreter" />
        <meta name="keywords" content="sign language, ASL, accessibility, AI, AWS, Bedrock, interpretation" />
        <meta name="author" content="SignBridge Team" />
        
        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content="SignBridge - Real-time Sign Language Interpreter" />
        <meta property="og:description" content="Break communication barriers with AI-powered sign language interpretation" />
        
        {/* Twitter */}
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:title" content="SignBridge - Real-time Sign Language Interpreter" />
        <meta property="twitter:description" content="Break communication barriers with AI-powered sign language interpretation" />
        
        {/* Fonts */}
        <link
          rel="preconnect"
          href="https://fonts.googleapis.com"
        />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"
          rel="stylesheet"
        />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}