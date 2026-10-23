import React, { useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Box } from '@mui/material';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

import Overview from './pages/Overview';
import SingleAnalyzer from './pages/SingleAnalyzer';
import BatchAnalysis from './pages/BatchAnalysis';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import AnalysisHistory from './pages/AnalysisHistory';
import ModelComparison from './pages/ModelComparison';
import Explainability from './pages/Explainability';
import NlpLaboratory from './pages/NlpLaboratory';

const industrialDarkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1',
      light: '#818cf8',
      dark: '#4f46e5',
    },
    secondary: {
      main: '#06b6d4',
    },
    background: {
      default: '#09090b',
      paper: '#121215',
    },
    text: {
      primary: '#f4f4f5',
      secondary: '#a1a1aa',
    },
    error: {
      main: '#f43f5e',
    },
    warning: {
      main: '#f59e0b',
    },
    success: {
      main: '#10b981',
    },
    info: {
      main: '#3b82f6',
    },
    divider: '#27272a',
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');

  const renderActivePage = () => {
    switch (activeTab) {
      case 'overview':
        return <Overview onNavigate={setActiveTab} />;
      case 'single':
        return <SingleAnalyzer />;
      case 'batch':
        return <BatchAnalysis />;
      case 'dashboard':
        return <AnalyticsDashboard onNavigate={setActiveTab} />;
      case 'history':
        return <AnalysisHistory />;
      case 'comparison':
        return <ModelComparison />;
      case 'explain':
        return <Explainability />;
      case 'lab':
        return <NlpLaboratory />;
      default:
        return <Overview onNavigate={setActiveTab} />;
    }
  };

  return (
    <ThemeProvider theme={industrialDarkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--bg-app)' }}>
        <Navbar />

        <Box sx={{ display: 'flex', flexGrow: 1 }}>
          <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
          
          <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, md: 3 }, overflowY: 'auto', minWidth: 0 }}>
            {renderActivePage()}
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}
