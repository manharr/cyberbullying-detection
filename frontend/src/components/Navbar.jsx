import React, { useEffect, useState } from 'react';
import {
  AppBar, Toolbar, Typography, Box
} from '@mui/material';
import TerminalIcon from '@mui/icons-material/Terminal';
import { checkHealth } from '../api/client';

export default function Navbar() {
  const [health, setHealth] = useState({ status: 'checking', models_loaded: false });

  useEffect(() => {
    checkHealth()
      .then(res => setHealth(res))
      .catch(() => setHealth({ status: 'offline', models_loaded: false }));
    const timer = setInterval(() => {
      checkHealth()
        .then(res => setHealth(res))
        .catch(() => setHealth({ status: 'offline', models_loaded: false }));
    }, 15000);
    return () => clearInterval(timer);
  }, []);

  const isHealthy = health.models_loaded;

  return (
    <AppBar
      position="sticky"
      sx={{
        background: '#0e0e11',
        borderBottom: '1px solid var(--border-subtle)',
        boxShadow: 'none',
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, md: 3 }, minHeight: '56px !important' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 32,
              height: 32,
              borderRadius: '6px',
              background: '#1e1b4b',
              border: '1px solid #312e81',
            }}
          >
            <TerminalIcon sx={{ color: '#818cf8', fontSize: 18 }} />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, letterSpacing: '-0.02em', fontSize: '0.95rem' }}>
              CyberShield
            </Typography>
            <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 500 }}>
              NLP Toxicity Engine
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.8,
              px: 1.2,
              py: 0.4,
              borderRadius: '20px',
              background: isHealthy ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
              border: `1px solid ${isHealthy ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)'}`,
            }}
          >
            <Box
              sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                backgroundColor: isHealthy ? '#10b981' : '#ef4444',
              }}
            />
            <Typography
              variant="caption"
              sx={{
                color: isHealthy ? '#34d399' : '#fca5a5',
                fontWeight: 600,
                fontSize: '0.72rem',
              }}
            >
              {isHealthy ? 'Models Ready' : 'Offline'}
            </Typography>
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
