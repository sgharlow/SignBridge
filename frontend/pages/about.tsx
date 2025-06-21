import Head from 'next/head'
import Link from 'next/link'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material'
import {
  ArrowBack,
  Cloud,
  Speed,
  Accessibility,
  School,
  LocalHospital,
  Psychology,
} from '@mui/icons-material'

export default function About() {
  return (
    <>
      <Head>
        <title>About SignToMe - AI Sign Language Interpreter</title>
        <meta name="description" content="Learn about SignToMe's mission to break communication barriers using AI" />
      </Head>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box mb={4}>
          <Link href="/" passHref>
            <Button startIcon={<ArrowBack />} sx={{ mb: 2 }}>
              Back to Interpreter
            </Button>
          </Link>
          
          <Typography variant="h2" component="h1" gutterBottom>
            About SignToMe
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Breaking communication barriers with AI-powered sign language interpretation
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {/* Mission */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom color="primary">
                  Our Mission
                </Typography>
                <Typography variant="body1" paragraph>
                  SignToMe is designed to bridge the communication gap between the deaf/hard-of-hearing 
                  community and hearing individuals through real-time, AI-powered sign language interpretation.
                </Typography>
                <Typography variant="body1" paragraph>
                  By leveraging cutting-edge AWS technology, we provide accessible, immediate translation 
                  services that can be used anywhere, anytime.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Technology */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom color="primary">
                  <Cloud sx={{ mr: 1 }} />
                  Technology Stack
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText
                      primary="Amazon Bedrock"
                      secondary="Claude 3.5 Sonnet for AI vision and interpretation"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="AWS IoT Greengrass"
                      secondary="Edge computing for low-latency processing"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Next.js & React"
                      secondary="Modern web interface with real-time capabilities"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="WebRTC & Canvas API"
                      secondary="Real-time video capture and processing"
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Key Features */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom color="primary">
                Key Features
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6} md={4}>
                  <Box textAlign="center">
                    <Speed color="primary" sx={{ fontSize: 48, mb: 1 }} />
                    <Typography variant="h6" gutterBottom>
                      Real-time Processing
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Sub-2 second latency from sign to text translation
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Box textAlign="center">
                    <Accessibility color="primary" sx={{ fontSize: 48, mb: 1 }} />
                    <Typography variant="h6" gutterBottom>
                      Accessibility First
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Built with WCAG guidelines and screen reader support
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Box textAlign="center">
                    <Psychology color="primary" sx={{ fontSize: 48, mb: 1 }} />
                    <Typography variant="h6" gutterBottom>
                      AI-Powered
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Advanced computer vision and natural language processing
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Use Cases */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom color="primary">
                  Real-World Applications
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Box display="flex" alignItems="flex-start" gap={2}>
                      <School color="primary" />
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          Education
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Enable inclusive classrooms where deaf and hearing students can 
                          communicate seamlessly during lectures, discussions, and group work.
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Box display="flex" alignItems="flex-start" gap={2}>
                      <LocalHospital color="primary" />
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          Healthcare
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Improve patient-provider communication in medical settings, 
                          ensuring accurate health information exchange.
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Hackathon Info */}
          <Grid item xs={12}>
            <Paper 
              sx={{ 
                p: 3, 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white'
              }}
            >
              <Box textAlign="center">
                <Typography variant="h5" gutterBottom>
                  AWS Breaking Barriers Hackathon 2025
                </Typography>
                <Typography variant="body1" paragraph>
                  SignToMe was developed as part of the AWS Breaking Barriers Virtual Challenge, 
                  demonstrating how generative AI and edge computing can create meaningful 
                  accessibility solutions.
                </Typography>
                <Box display="flex" justifyContent="center" gap={2} flexWrap="wrap">
                  <Chip label="Amazon Bedrock" variant="outlined" sx={{ color: 'white', borderColor: 'white' }} />
                  <Chip label="IoT Greengrass" variant="outlined" sx={{ color: 'white', borderColor: 'white' }} />
                  <Chip label="Edge Computing" variant="outlined" sx={{ color: 'white', borderColor: 'white' }} />
                  <Chip label="Accessibility" variant="outlined" sx={{ color: 'white', borderColor: 'white' }} />
                </Box>
              </Box>
            </Paper>
          </Grid>

          {/* Call to Action */}
          <Grid item xs={12}>
            <Box textAlign="center">
              <Link href="/" passHref>
                <Button variant="contained" size="large" sx={{ mt: 2 }}>
                  Try SignToMe Now
                </Button>
              </Link>
            </Box>
          </Grid>
        </Grid>
      </Container>
    </>
  )
}