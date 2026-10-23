import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, CircularProgress,
  Alert, Chip, TextField, Button, Table,
  TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper
} from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip,
  ResponsiveContainer
} from 'recharts';
import { getGlobalExplanations, analyzeComment } from '../api/client';

export default function Explainability() {
  const [globalData, setGlobalData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [sandboxText, setSandboxText] = useState('you are not stupid, you are very helpful');
  const [sandboxResult, setSandboxResult] = useState(null);
  const [sandboxLoading, setSandboxLoading] = useState(false);

  useEffect(() => {
    getGlobalExplanations(12)
      .then(res => setGlobalData(res))
      .catch(() => setError('Failed to retrieve feature weights.'))
      .finally(() => setLoading(false));
  }, []);

  const handleTestSandbox = async () => {
    if (!sandboxText.trim()) return;
    setSandboxLoading(true);
    try {
      const res = await analyzeComment(sandboxText, false);
      setSandboxResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setSandboxLoading(false);
    }
  };

  useEffect(() => {
    handleTestSandbox();
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress size={30} sx={{ color: '#818cf8' }} />
      </Box>
    );
  }

  const toxicFeatures = (globalData?.top_toxic_indicators || []).slice(0, 10).reverse();
  const nonToxicFeatures = (globalData?.top_non_toxic_indicators || []).slice(0, 10).reverse();

  return (
    <Box sx={{ p: { xs: 1, md: 2 } }} className="animate-fade-in">
      <Box sx={{ mb: 2.5 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          Explainable AI (XAI) & Feature Weights
        </Typography>
        <Typography variant="caption" sx={{ color: 'var(--text-secondary)' }}>
          Learned linear model coefficients and local term-by-term additive contributions.
        </Typography>
      </Box>

      {/* Global Charts */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#f43f5e', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1 }}>
              Top Toxic Indicators (+ Coefficients)
            </Typography>
            <Box sx={{ width: '100%', height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={toxicFeatures} layout="vertical" margin={{ top: 5, right: 20, left: 35, bottom: 5 }}>
                  <XAxis type="number" stroke="#71717a" fontSize={10} />
                  <YAxis type="category" dataKey="word" stroke="#71717a" fontSize={11} />
                  <RechartsTooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: 6, fontSize: 12 }} />
                  <Bar dataKey="weight" fill="#f43f5e" radius={[0, 3, 3, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={12} md={6}>
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1 }}>
              Top Civil Indicators (- Coefficients)
            </Typography>
            <Box sx={{ width: '100%', height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={nonToxicFeatures} layout="vertical" margin={{ top: 5, right: 20, left: 35, bottom: 5 }}>
                  <XAxis type="number" stroke="#71717a" fontSize={10} />
                  <YAxis type="category" dataKey="word" stroke="#71717a" fontSize={11} />
                  <RechartsTooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: 6, fontSize: 12 }} />
                  <Bar dataKey="weight" fill="#10b981" radius={[0, 3, 3, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Box>
        </Grid>
      </Grid>

      {/* Local Attribution Sandbox */}
      <Box className="glass-panel" sx={{ p: 2 }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
          Local Attribution Sandbox: Contribution = TF-IDF × Weight
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <TextField
            fullWidth
            size="small"
            value={sandboxText}
            onChange={(e) => setSandboxText(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: '#fff',
                backgroundColor: 'rgba(0, 0, 0, 0.3)',
                borderRadius: '6px',
                fontSize: '0.88rem',
                '& fieldset': { borderColor: 'var(--border-subtle)' },
              }
            }}
          />
          <Button
            variant="contained"
            size="small"
            onClick={handleTestSandbox}
            disabled={sandboxLoading || !sandboxText.trim()}
            sx={{ backgroundColor: '#6366f1', px: 2 }}
          >
            {sandboxLoading ? '...' : 'Compute'}
          </Button>
        </Box>

        {sandboxResult && (
          <TableContainer component={Paper} sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ '& th': { color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.74rem', borderColor: 'var(--border-subtle)' } }}>
                  <TableCell>Term</TableCell>
                  <TableCell align="center">TF-IDF</TableCell>
                  <TableCell align="center">Model Weight</TableCell>
                  <TableCell align="center">Net Contribution</TableCell>
                  <TableCell align="center">Polarity</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sandboxResult.influential_words && sandboxResult.influential_words.length > 0 ? (
                  sandboxResult.influential_words.map((item, idx) => (
                    <TableRow key={idx} sx={{ '& td': { color: '#e4e4e7', fontSize: '0.8rem', borderColor: 'var(--border-subtle)' } }}>
                      <TableCell sx={{ fontFamily: 'monospace', fontWeight: 600 }}>{item.word}</TableCell>
                      <TableCell align="center">{item.tfidf_value}</TableCell>
                      <TableCell align="center">{item.model_weight}</TableCell>
                      <TableCell align="center" sx={{ fontWeight: 700, color: item.contribution > 0 ? '#f43f5e' : '#10b981' }}>
                        {item.contribution > 0 ? `+${item.contribution}` : item.contribution}
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={item.polarity === 'toxic' ? 'Toxic' : 'Civil'}
                          size="small"
                          className={item.polarity === 'toxic' ? 'polarity-toxic' : 'polarity-safe'}
                          sx={{ fontSize: '0.68rem', borderRadius: '4px' }}
                        />
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={5} sx={{ textAlign: 'center', py: 2, color: 'var(--text-muted)' }}>
                      No dictionary vocabulary matched.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Box>
  );
}
