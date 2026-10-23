import React from 'react';
import {
  List, ListItem, ListItemButton, ListItemIcon,
  ListItemText, Typography, Box
} from '@mui/material';
import SpaceDashboardOutlinedIcon from '@mui/icons-material/SpaceDashboardOutlined';
import EditNoteOutlinedIcon from '@mui/icons-material/EditNoteOutlined';
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined';
import BarChartOutlinedIcon from '@mui/icons-material/BarChartOutlined';
import HistoryToggleOffOutlinedIcon from '@mui/icons-material/HistoryToggleOffOutlined';
import TuneOutlinedIcon from '@mui/icons-material/TuneOutlined';
import PsychologyOutlinedIcon from '@mui/icons-material/PsychologyOutlined';
import ScienceOutlinedIcon from '@mui/icons-material/ScienceOutlined';

const navItems = [
  { id: 'overview', label: 'Overview', icon: <SpaceDashboardOutlinedIcon sx={{ fontSize: 18 }} /> },
  { id: 'single', label: 'Analyzer', icon: <EditNoteOutlinedIcon sx={{ fontSize: 18 }} /> },
  { id: 'batch', label: 'Batch Processing', icon: <CloudUploadOutlinedIcon sx={{ fontSize: 18 }} /> },
  { id: 'dashboard', label: 'Analytics', icon: <BarChartOutlinedIcon sx={{ fontSize: 18 }} /> },
  { id: 'history', label: 'History', icon: <HistoryToggleOffOutlinedIcon sx={{ fontSize: 18 }} /> },
  { id: 'comparison', label: 'Model Benchmarks', icon: <TuneOutlinedIcon sx={{ fontSize: 18 }} /> },
  { id: 'explain', label: 'Explainability', icon: <PsychologyOutlinedIcon sx={{ fontSize: 18 }} /> },
  { id: 'lab', label: 'NLP Lab', icon: <ScienceOutlinedIcon sx={{ fontSize: 18 }} /> },
];

export default function Sidebar({ activeTab, setActiveTab }) {
  return (
    <Box
      sx={{
        width: 220,
        flexShrink: 0,
        borderRight: '1px solid var(--border-subtle)',
        background: '#0d0d10',
        display: 'flex',
        flexDirection: 'column',
        minHeight: 'calc(100vh - 56px)',
      }}
    >
      <Box sx={{ p: 1.5, pb: 0.5 }}>
        <Typography
          variant="caption"
          sx={{
            color: 'var(--text-muted)',
            fontWeight: 700,
            letterSpacing: '0.06em',
            fontSize: '0.68rem',
            px: 1,
            textTransform: 'uppercase',
          }}
        >
          Navigation
        </Typography>
      </Box>

      <List sx={{ px: 1, py: 0.5 }}>
        {navItems.map((item) => {
          const isSelected = activeTab === item.id;
          return (
            <ListItem key={item.id} disablePadding sx={{ mb: 0.2 }}>
              <ListItemButton
                onClick={() => setActiveTab(item.id)}
                sx={{
                  borderRadius: '6px',
                  py: 0.7,
                  px: 1.2,
                  backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.12)' : 'transparent',
                  border: isSelected ? '1px solid rgba(99, 102, 241, 0.25)' : '1px solid transparent',
                  color: isSelected ? '#e0e7ff' : 'var(--text-secondary)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.03)',
                    color: '#fff',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 28,
                    color: isSelected ? '#818cf8' : 'var(--text-muted)',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontSize: '0.82rem',
                    fontWeight: isSelected ? 600 : 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Box sx={{ mt: 'auto', p: 1.5 }}>
        <Box
          sx={{
            p: 1.2,
            borderRadius: '6px',
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <Typography variant="caption" sx={{ color: 'var(--text-secondary)', fontWeight: 600, display: 'block', fontSize: '0.72rem' }}>
            MCA NLP Project
          </Typography>
          <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontSize: '0.68rem', display: 'block' }}>
            Linear SVM Engine
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
