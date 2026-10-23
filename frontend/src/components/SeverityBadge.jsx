import React from 'react';
import { Box, Typography } from '@mui/material';

const severityConfig = {
  0: { label: 'None', color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)', border: 'rgba(16, 185, 129, 0.25)' },
  1: { label: 'Low', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.25)' },
  2: { label: 'Moderate', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)', border: 'rgba(245, 158, 11, 0.25)' },
  3: { label: 'High', color: '#f43f5e', bg: 'rgba(244, 63, 94, 0.12)', border: 'rgba(244, 63, 94, 0.3)' },
};

export default function SeverityBadge({ level = 0 }) {
  const conf = severityConfig[level] || severityConfig[0];

  return (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 0.8,
        px: 1,
        py: 0.3,
        borderRadius: '16px',
        backgroundColor: conf.bg,
        border: `1px solid ${conf.border}`,
      }}
    >
      <Box
        sx={{
          width: 6,
          height: 6,
          borderRadius: '50%',
          backgroundColor: conf.color,
        }}
      />
      <Typography
        variant="caption"
        sx={{
          color: conf.color,
          fontWeight: 600,
          fontSize: '0.74rem',
          lineHeight: 1,
        }}
      >
        {conf.label}
      </Typography>
    </Box>
  );
}
