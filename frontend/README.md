# SignToMe Frontend

Real-time sign language interpreter web application built with Next.js and React.

## Features

- **Real-time Video Capture**: Uses WebRTC to access device camera
- **Live Translation**: Processes video frames every 2 seconds using AWS Bedrock
- **Text-to-Speech**: Speaks translations aloud for accessibility
- **Translation History**: Keeps track of recent interpretations
- **Responsive Design**: Works on desktop and mobile devices
- **Accessibility**: Built with WCAG guidelines and screen reader support

## Technology Stack

- **Next.js 14**: React framework with TypeScript
- **Material-UI (MUI)**: Component library for consistent design
- **WebRTC**: Real-time video capture
- **Canvas API**: Frame extraction and image processing
- **Web Speech API**: Text-to-speech functionality

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Modern web browser with camera access

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your API endpoint

# Start development server
npm run dev
```

### Environment Variables

- `NEXT_PUBLIC_API_ENDPOINT`: AWS API Gateway endpoint for sign processing

## Usage

1. **Start Camera**: Click "Start Camera" to begin video capture
2. **Position Yourself**: Ensure you're clearly visible in the camera view
3. **Sign**: Perform ASL signs slowly and clearly
4. **View Results**: Translations appear in real-time on the right panel
5. **Listen**: Click any translation to hear it spoken aloud

## Components

### Main Components

- `pages/index.tsx`: Main application page with video capture
- `pages/about.tsx`: Information about the project
- `components/TranslationDisplay.tsx`: Shows current and recent translations
- `components/VideoProcessor.tsx`: Handles video frame capture

### Utilities

- `utils/api.ts`: API client for backend communication
- `utils/speech.ts`: Text-to-speech service wrapper

## API Integration

The frontend communicates with the AWS Lambda backend via REST API:

```typescript
POST /process
{
  "frame_data": "base64_encoded_image",
  "timestamp": "2025-06-21T12:00:00Z",
  "device_id": "web-interface"
}
```

Response:
```typescript
{
  "translation": "Hello",
  "confidence": 0.85,
  "timestamp": "2025-06-21T12:00:00Z",
  "device_id": "web-interface"
}
```

## Performance Optimization

- Frame capture limited to 2-second intervals
- JPEG compression at 80% quality
- Canvas reuse for memory efficiency
- Debounced API calls to prevent overload

## Accessibility Features

- Screen reader compatible
- Keyboard navigation support
- High contrast text display
- Text-to-speech for all translations
- ARIA labels and semantic HTML

## Browser Compatibility

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

Requires:
- WebRTC support
- Canvas API
- ES2020 JavaScript features
- Web Speech API (optional, for text-to-speech)

## Deployment

### Development
```bash
npm run dev
```

### Production
```bash
npm run build
npm start
```

### Static Export
```bash
npm run build
npm run export
```

## Project Structure

```
frontend/
├── components/          # Reusable React components
├── pages/              # Next.js pages
├── public/             # Static assets
├── utils/              # Utility functions and services
├── styles/             # CSS styles
├── types/              # TypeScript type definitions
└── package.json        # Dependencies and scripts
```

## Contributing

This project was built for the AWS Breaking Barriers Hackathon 2025. 

## License

MIT License - see LICENSE file for details.