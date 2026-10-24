import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Chip,
  CircularProgress, Alert, Stack
} from '@mui/material';
import TuneIcon from '@mui/icons-material/Tune';
import { getModelComparison, getModelMetrics } from '../api/client';

export default function ModelComparison() {
  const [data, setData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([getModelComparison(), getModelMetrics()])
      .then(([compRes, metricsRes]) => {
        setData(compRes);
        setMetrics(metricsRes);
      })
      .catch(() => setError('Failed to load benchmark metrics.'))
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

  const valComp = data?.model_comparison?.validation_comparison || {};
  const bestModelName = data?.model_comparison?.selected_best_model || 'Linear SVM';
  const experiments = data?.preprocessing_experiments?.experiments || [];
  const testEval = metrics?.evaluation?.held_out_test_metrics;

  return (
    <Box sx={{ p: { xs: 1, md: 2 } }} className="animate-fade-in">
      <Box sx={{ mb: 2.5 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          Model Benchmarks & Empirical Experiments
        </Typography>
        <Typography variant="caption" sx={{ color: 'var(--text-secondary)' }}>
          Validation benchmarks and held-out test evaluations on Kaggle Jigsaw Toxic records.
        </Typography>
      </Box>

      {/* Model Benchmark Table */}
      <Box className="glass-panel" sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
          <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
            Traditional Classifier Validation (5,250 records)
          </Typography>
          <Chip label={`Selected: ${bestModelName}`} size="small" sx={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', fontWeight: 600, fontSize: '0.72rem' }} />
        </Box>

        <TableContainer component={Paper} sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ '& th': { color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.75rem', borderColor: 'var(--border-subtle)' } }}>
                <TableCell>Algorithm</TableCell>
                <TableCell align="center">Accuracy</TableCell>
                <TableCell align="center">Precision</TableCell>
                <TableCell align="center">Recall</TableCell>
                <TableCell align="center">Macro F1</TableCell>
                <TableCell align="center">Toxic F1</TableCell>
                <TableCell align="center">Latency</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(valComp).map(([name, m]) => {
                const isSelected = name === bestModelName;
                return (
                  <TableRow
                    key={name}
                    sx={{
                      backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.06)' : 'transparent',
                      '& td': { color: '#e4e4e7', fontSize: '0.82rem', borderColor: 'var(--border-subtle)' }
                    }}
                  >
                    <TableCell sx={{ fontWeight: isSelected ? 700 : 500 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8, flexWrap: 'wrap' }}>
                        <span>{name}</span>
                        {m.is_optional && (
                          <Chip
                            label="Optional Transformer"
                            size="small"
                            sx={{
                              fontSize: '0.65rem',
                              height: 18,
                              background: 'rgba(168, 85, 247, 0.15)',
                              color: '#c084fc',
                              border: '1px solid rgba(168, 85, 247, 0.3)'
                            }}
                          />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell align="center">{(m.accuracy * 100).toFixed(1)}%</TableCell>
                    <TableCell align="center">{(m.precision_macro * 100).toFixed(1)}%</TableCell>
                    <TableCell align="center">{(m.recall_macro * 100).toFixed(1)}%</TableCell>
                    <TableCell align="center" sx={{ color: isSelected ? '#818cf8' : '#fff', fontWeight: 700 }}>
                      {m.f1_macro.toFixed(4)}
                    </TableCell>
                    <TableCell align="center" sx={{ color: '#f43f5e', fontWeight: 600 }}>
                      {m.class_1_toxic?.f1?.toFixed(4)}
                    </TableCell>
                    <TableCell align="center" sx={{ fontFamily: 'monospace', color: 'var(--text-muted)' }}>
                      {m.per_sample_latency_ms ? `${m.per_sample_latency_ms.toFixed(1)}ms` : `${m.training_time_seconds}s`}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>

      {/* Threshold Tuning Section */}
      {data?.model_comparison?.threshold_tuning && (
        <Box className="glass-panel" sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', sm: 'center' }, gap: 1, mb: 1.5 }}>
            <Box>
              <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <TuneIcon sx={{ fontSize: 14 }} /> DistilBERT Cost-Sensitive Threshold Tuning
              </Typography>
              <Typography variant="body2" sx={{ color: 'var(--text-secondary)', fontSize: '0.8rem', mt: 0.2 }}>
                Calibrating decision thresholds on validation data balances precision and toxic recall on class-imbalanced corpora.
              </Typography>
            </Box>
            <Chip
              label={`Optimal Threshold: ${data.model_comparison.threshold_tuning.optimal_threshold}`}
              size="small"
              sx={{ background: 'rgba(168, 85, 247, 0.2)', color: '#c084fc', fontWeight: 700, fontSize: '0.74rem' }}
            />
          </Box>

          {/* Metric Gain Summary Cards */}
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={4}>
              <Box sx={{ p: 1.2, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>MACRO F1 (DEFAULT 0.50 vs OPTIMAL {data.model_comparison.threshold_tuning.optimal_threshold})</Typography>
                <Stack direction="row" spacing={1} alignItems="baseline" sx={{ mt: 0.3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#c084fc' }}>
                    {data.model_comparison.threshold_tuning.f1_macro_optimal.toFixed(4)}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 600 }}>
                    (+{(data.model_comparison.threshold_tuning.f1_macro_optimal - data.model_comparison.threshold_tuning.f1_macro_default).toFixed(4)})
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>
                    from {data.model_comparison.threshold_tuning.f1_macro_default.toFixed(4)}
                  </Typography>
                </Stack>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box sx={{ p: 1.2, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>TOXIC CLASS F1 (F1-SCORE)</Typography>
                <Stack direction="row" spacing={1} alignItems="baseline" sx={{ mt: 0.3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#f43f5e' }}>
                    {data.model_comparison.threshold_tuning.toxic_f1_optimal.toFixed(4)}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 600 }}>
                    (+{(data.model_comparison.threshold_tuning.toxic_f1_optimal - data.model_comparison.threshold_tuning.toxic_f1_default).toFixed(4)})
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>
                    from {data.model_comparison.threshold_tuning.toxic_f1_default.toFixed(4)}
                  </Typography>
                </Stack>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box sx={{ p: 1.2, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>ARCHITECTURAL RATIONALE</Typography>
                <Typography variant="caption" sx={{ display: 'block', color: 'var(--text-secondary)', fontSize: '0.72rem', mt: 0.4 }}>
                  Linear SVM is retained as production champion for &lt;2ms CPU latency and closed-form XAI. DistilBERT provides deep contextual representations with threshold tuning.
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Threshold Tuning Curve Table */}
          {data.model_comparison.threshold_tuning.curve_samples && (
            <TableContainer component={Paper} sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ '& th': { color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.72rem', borderColor: 'var(--border-subtle)' } }}>
                    <TableCell>Decision Threshold</TableCell>
                    <TableCell align="center">Accuracy</TableCell>
                    <TableCell align="center">Toxic Precision</TableCell>
                    <TableCell align="center">Toxic Recall</TableCell>
                    <TableCell align="center">Toxic F1</TableCell>
                    <TableCell align="center">Macro F1</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.model_comparison.threshold_tuning.curve_samples.filter((_, idx) => idx % 2 === 0 || idx === data.model_comparison.threshold_tuning.curve_samples.length - 1).map((sample, idx) => {
                    const isOptimal = Math.abs(sample.threshold - data.model_comparison.threshold_tuning.optimal_threshold) < 0.01;
                    return (
                      <TableRow
                        key={idx}
                        sx={{
                          backgroundColor: isOptimal ? 'rgba(168, 85, 247, 0.1)' : 'transparent',
                          '& td': { color: '#e4e4e7', fontSize: '0.78rem', borderColor: 'var(--border-subtle)' }
                        }}
                      >
                        <TableCell sx={{ fontWeight: isOptimal ? 800 : 500, color: isOptimal ? '#c084fc' : '#e4e4e7' }}>
                          {sample.threshold.toFixed(2)} {isOptimal ? '★ (Optimal F1)' : sample.threshold === 0.50 ? '(Default)' : ''}
                        </TableCell>
                        <TableCell align="center">{(sample.accuracy * 100).toFixed(1)}%</TableCell>
                        <TableCell align="center">{(sample.toxic_precision * 100).toFixed(1)}%</TableCell>
                        <TableCell align="center">{(sample.toxic_recall * 100).toFixed(1)}%</TableCell>
                        <TableCell align="center" sx={{ color: '#f43f5e', fontWeight: isOptimal ? 700 : 500 }}>
                          {sample.toxic_f1.toFixed(4)}
                        </TableCell>
                        <TableCell align="center" sx={{ color: isOptimal ? '#c084fc' : '#818cf8', fontWeight: isOptimal ? 800 : 600 }}>
                          {sample.f1_macro.toFixed(4)}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      )}

      {/* Held-Out Confusion Matrix */}
      {testEval && (
        <Box className="glass-panel" sx={{ p: 2, mb: 3 }}>
          <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
            Held-Out Test Set (5,250 Unseen Records)
          </Typography>

          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <Stack spacing={1}>
                <Box sx={{ p: 1, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>ACCURACY</Typography>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>{(testEval.accuracy * 100).toFixed(2)}%</Typography>
                </Box>
                <Box sx={{ p: 1, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>MACRO F1</Typography>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#818cf8' }}>{testEval.f1_macro.toFixed(4)}</Typography>
                </Box>
                <Box sx={{ p: 1, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>TOXIC CLASS F1</Typography>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#f43f5e' }}>{testEval.class_1_toxic?.f1?.toFixed(4)}</Typography>
                </Box>
              </Stack>
            </Grid>

            <Grid item xs={12} sm={8}>
              <Box sx={{ maxWidth: 380, mx: 'auto', p: 1.5, borderRadius: '8px', background: 'rgba(0, 0, 0, 0.3)', border: '1px solid var(--border-subtle)' }}>
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Box sx={{ p: 1.2, borderRadius: '6px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', textAlign: 'center' }}>
                      <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 600, fontSize: '0.7rem' }}>TRUE NEG (TN)</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 800, color: '#10b981' }}>{testEval.confusion_matrix?.tn}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ p: 1.2, borderRadius: '6px', background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)', textAlign: 'center' }}>
                      <Typography variant="caption" sx={{ color: '#f59e0b', fontWeight: 600, fontSize: '0.7rem' }}>FALSE POS (FP)</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 800, color: '#f59e0b' }}>{testEval.confusion_matrix?.fp}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ p: 1.2, borderRadius: '6px', background: 'rgba(244, 63, 94, 0.08)', border: '1px solid rgba(244, 63, 94, 0.25)', textAlign: 'center' }}>
                      <Typography variant="caption" sx={{ color: '#f43f5e', fontWeight: 600, fontSize: '0.7rem' }}>FALSE NEG (FN)</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 800, color: '#f43f5e' }}>{testEval.confusion_matrix?.fn}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ p: 1.2, borderRadius: '6px', background: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.25)', textAlign: 'center' }}>
                      <Typography variant="caption" sx={{ color: '#818cf8', fontWeight: 600, fontSize: '0.7rem' }}>TRUE POS (TP)</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 800, color: '#818cf8' }}>{testEval.confusion_matrix?.tp}</Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Preprocessing Ablation Study */}
      <Box className="glass-panel" sx={{ p: 2 }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
          Feature Engineering & Preprocessing Ablation
        </Typography>

        <TableContainer component={Paper} sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ '& th': { color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.75rem', borderColor: 'var(--border-subtle)' } }}>
                <TableCell>Stage</TableCell>
                <TableCell align="center">Accuracy</TableCell>
                <TableCell align="center">Macro F1</TableCell>
                <TableCell align="center">Toxic F1</TableCell>
                <TableCell align="center">Time</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {experiments.map((exp, idx) => (
                <TableRow
                  key={idx}
                  sx={{ '& td': { color: '#e4e4e7', fontSize: '0.8rem', borderColor: 'var(--border-subtle)' } }}
                >
                  <TableCell sx={{ fontWeight: 600 }}>{exp.experiment_name}</TableCell>
                  <TableCell align="center">{(exp.accuracy * 100).toFixed(1)}%</TableCell>
                  <TableCell align="center" sx={{ fontWeight: 700, color: '#818cf8' }}>{exp.macro_f1.toFixed(4)}</TableCell>
                  <TableCell align="center" sx={{ color: '#f43f5e' }}>{exp.toxic_class_f1.toFixed(4)}</TableCell>
                  <TableCell align="center" sx={{ fontFamily: 'monospace', color: 'var(--text-muted)' }}>{exp.training_time_seconds}s</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
}
