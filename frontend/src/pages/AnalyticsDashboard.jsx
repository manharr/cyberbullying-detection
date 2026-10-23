import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, CircularProgress,
  Alert, Button, Chip, Stack
} from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import RefreshIcon from '@mui/icons-material/Refresh';
import SeverityBadge from '../components/SeverityBadge';
import { getDashboardStats } from '../api/client';

export default function AnalyticsDashboard({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (err) {
      setError('Telemetry offline.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress size={30} sx={{ color: '#818cf8' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  const pieData = [
    { name: 'Non-toxic', value: stats.non_toxic_count || 0, color: '#10b981' },
    { name: 'Toxic', value: stats.toxic_count || 0, color: '#f43f5e' },
  ];

  const severityData = [
    { name: 'L0 (None)', count: stats.severity_distribution?.[0] || 0, fill: '#10b981' },
    { name: 'L1 (Low)', count: stats.severity_distribution?.[1] || 0, fill: '#3b82f6' },
    { name: 'L2 (Moderate)', count: stats.severity_distribution?.[2] || 0, fill: '#f59e0b' },
    { name: 'L3 (High)', count: stats.severity_distribution?.[3] || 0, fill: '#f43f5e' },
  ];

  const categoryData = Object.entries(stats.category_breakdown || {}).map(([key, val]) => ({
    name: key.replace('_', ' ').toUpperCase(),
    count: val,
  }));

  return (
    <Box sx={{ p: { xs: 1, md: 2 } }} className="animate-fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2.5 }}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
            System Telemetry & Analytics
          </Typography>
          <Typography variant="caption" sx={{ color: 'var(--text-secondary)' }}>
            Real-time SQLite database statistics and inference counts.
          </Typography>
        </Box>
        <Button
          startIcon={<RefreshIcon sx={{ fontSize: 16 }} />}
          onClick={fetchStats}
          variant="outlined"
          size="small"
          sx={{ borderColor: 'var(--border-subtle)', color: 'var(--text-secondary)' }}
        >
          Refresh
        </Button>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}>
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.68rem' }}>
              TOTAL ANALYSES
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 700, mt: 0.5 }}>
              {stats.total_analyses}
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} md={3}>
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#f43f5e', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.68rem' }}>
              TOXIC DETECTED
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#f43f5e', mt: 0.5 }}>
              {stats.toxic_count} <Typography component="span" variant="caption" sx={{ color: 'var(--text-muted)' }}>({stats.toxic_percentage}%)</Typography>
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} md={3}>
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.68rem' }}>
              CLEAN / NON-TOXIC
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#10b981', mt: 0.5 }}>
              {stats.non_toxic_count}
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6} md={3}>
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#818cf8', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.68rem' }}>
              CHAMPION F1 SCORE
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#818cf8', mt: 0.5 }}>
              83.9%
            </Typography>
          </Box>
        </Grid>
      </Grid>

      {/* Charts Grid */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Box className="glass-panel" sx={{ p: 2, height: '100%' }}>
            <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1 }}>
              Classification Split
            </Typography>
            <Box sx={{ width: '100%', height: 200 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={48} outerRadius={68} paddingAngle={4} dataKey="value">
                    {pieData.map((e, idx) => <Cell key={idx} fill={e.color} />)}
                  </Pie>
                  <RechartsTooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: 6, fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={12} md={8}>
          <Box className="glass-panel" sx={{ p: 2, height: '100%' }}>
            <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1 }}>
              Severity Level Distribution
            </Typography>
            <Box sx={{ width: '100%', height: 200 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={severityData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="#71717a" fontSize={11} />
                  <YAxis stroke="#71717a" fontSize={11} allowDecimals={false} />
                  <RechartsTooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: 6, fontSize: 12 }} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {severityData.map((e, idx) => <Cell key={idx} fill={e.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Box>
        </Grid>
      </Grid>

      {/* Categories */}
      <Box className="glass-panel" sx={{ p: 2 }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
          Category Activations
        </Typography>
        <Box sx={{ width: '100%', height: 180 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={categoryData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <XAxis dataKey="name" stroke="#71717a" fontSize={11} />
              <YAxis stroke="#71717a" fontSize={11} allowDecimals={false} />
              <RechartsTooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: 6, fontSize: 12 }} />
              <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </Box>
    </Box>
  );
}
