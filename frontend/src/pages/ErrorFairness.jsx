import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, CircularProgress,
  Alert, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, Stack
} from '@mui/material';
import { getErrorAnalysis, getFairnessAnalysis } from '../api/client';

export default function ErrorFairness() {
  const [errorData, setErrorData] = useState(null);
  const [fairnessData, setFairnessData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([getErrorAnalysis(), getFairnessAnalysis()])
      .then(([errRes, fairRes]) => {
        setErrorData(errRes);
        setFairnessData(fairRes);
      })
      .catch(() => setError('Failed to retrieve evaluation reports.'))
      .finally(() => setLoading(false));
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

  const identityGroups = fairnessData?.identity_subgroups || {};

  return (
    <Box sx={{ p: { xs: 1, md: 2 } }} className="animate-fade-in">
      <Box sx={{ mb: 2.5 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          Error Diagnostics & Algorithmic Fairness
        </Typography>
        <Typography variant="caption" sx={{ color: 'var(--text-secondary)' }}>
          Held-out error distributions, failure mode taxonomy, and identity subgroup FPR disparities.
        </Typography>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.68rem' }}>
              TEST RECORDS EVALUATED
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 700, mt: 0.5 }}>
              {errorData.total_test_evaluated}
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#f59e0b', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.68rem' }}>
              FALSE POSITIVE RATE (FPR)
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#f59e0b', mt: 0.5 }}>
              {(errorData.false_positive_rate * 100).toFixed(2)}%
            </Typography>
            <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>
              {errorData.false_positive_count} clean comments overflagged
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#f43f5e', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.68rem' }}>
              FALSE NEGATIVE RATE (FNR)
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#f43f5e', mt: 0.5 }}>
              {(errorData.false_negative_rate * 100).toFixed(2)}%
            </Typography>
            <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>
              {errorData.false_negative_count} toxic comments missed
            </Typography>
          </Box>
        </Grid>
      </Grid>

      {/* Failure Modes */}
      <Box className="glass-panel" sx={{ p: 2, mb: 3 }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
          Identified Linguistic Failure Modes
        </Typography>
        <Grid container spacing={1.5}>
          {errorData.failure_modes.map((fm, idx) => (
            <Grid item xs={12} md={4} key={idx}>
              <Box sx={{ p: 1.5, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)', height: '100%' }}>
                <Typography variant="caption" sx={{ fontWeight: 700, color: '#818cf8', display: 'block' }}>
                  {fm.pattern}
                </Typography>
                <Typography variant="caption" sx={{ color: 'var(--text-secondary)', display: 'block', my: 0.5 }}>
                  {fm.description}
                </Typography>
                <Typography variant="caption" sx={{ color: '#34d399', fontSize: '0.7rem' }}>
                  Fix: {fm.mitigation}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* FP vs FN Samples */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Box className="glass-panel" sx={{ p: 2, height: '100%' }}>
            <Typography variant="caption" sx={{ color: '#f59e0b', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
              False Positive Examples (Actual: Clean, Pred: Toxic)
            </Typography>
            <Stack spacing={1}>
              {errorData.fp_examples.slice(0, 3).map((ex, i) => (
                <Box key={i} sx={{ p: 1, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                  <Typography variant="caption" sx={{ color: '#e4e4e7', display: 'block', fontStyle: 'italic', mb: 0.3 }}>
                    "{ex.text}"
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#fbbf24', fontSize: '0.7rem' }}>
                    Cause: {ex.possible_cause}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Box>
        </Grid>

        <Grid item xs={12} md={6}>
          <Box className="glass-panel" sx={{ p: 2, height: '100%' }}>
            <Typography variant="caption" sx={{ color: '#f43f5e', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
              False Negative Examples (Actual: Toxic, Pred: Clean)
            </Typography>
            <Stack spacing={1}>
              {errorData.fn_examples.slice(0, 3).map((ex, i) => (
                <Box key={i} sx={{ p: 1, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                  <Typography variant="caption" sx={{ color: '#e4e4e7', display: 'block', fontStyle: 'italic', mb: 0.3 }}>
                    "{ex.text}"
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#f87171', fontSize: '0.7rem' }}>
                    Cause: {ex.possible_cause}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Box>
        </Grid>
      </Grid>

      {/* Identity Subgroup Disparity */}
      <Box className="glass-panel" sx={{ p: 2 }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
          Identity Subgroup False Positive Disparity (Baseline FPR: {(fairnessData.global_false_positive_rate * 100).toFixed(2)}%)
        </Typography>

        <TableContainer component={Paper} sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ '& th': { color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.74rem', borderColor: 'var(--border-subtle)' } }}>
                <TableCell>Category</TableCell>
                <TableCell>Matched Keywords</TableCell>
                <TableCell align="center">Matched Comments</TableCell>
                <TableCell align="center">Subgroup FPR</TableCell>
                <TableCell align="center">Disparity vs Global</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(identityGroups).map(([group, val]) => (
                <TableRow key={group} sx={{ '& td': { color: '#e4e4e7', fontSize: '0.8rem', borderColor: 'var(--border-subtle)' } }}>
                  <TableCell sx={{ fontWeight: 600 }}>{group}</TableCell>
                  <TableCell sx={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{val.terms_tracked.join(', ')}</TableCell>
                  <TableCell align="center">{val.total_matched_comments}</TableCell>
                  <TableCell align="center">{(val.subgroup_fpr * 100).toFixed(1)}%</TableCell>
                  <TableCell align="center">
                    <Chip
                      label={`${val.fpr_disparity_ratio}x`}
                      size="small"
                      sx={{
                        background: val.fpr_disparity_ratio > 1.5 ? 'rgba(244, 63, 94, 0.12)' : 'rgba(16, 185, 129, 0.12)',
                        color: val.fpr_disparity_ratio > 1.5 ? '#f43f5e' : '#10b981',
                        fontWeight: 600,
                        fontSize: '0.7rem',
                        borderRadius: '4px'
                      }}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}
