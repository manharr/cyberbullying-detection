import React from 'react';
import {
  Box, Typography, Grid, Paper, Divider, Stack
} from '@mui/material';

export default function AboutMethodology() {
  const members = [
    {
      role: 'Member 1 — NLP Pipeline & Data Discovery',
      name: 'Dataset & Preprocessing Lead',
      items: [
        'Safe dataset discovery, zip extraction & column validation.',
        'Stage A-C text sanitization, tokenization & negation preservation.',
        'Stage D-E WordNet lemmatization & Porter stemming ablation.',
        '6-stage feature engineering comparative study.'
      ]
    },
    {
      role: 'Member 2 — Machine Learning & Explainable AI',
      name: 'Model Engineering & XAI Lead',
      items: [
        'TF-IDF vectorizer configuration (unigrams + bigrams).',
        'Model training: Linear SVM (Calibrated), Logistic Regression, Naive Bayes.',
        '6 multi-label sub-category binary relevance classifiers.',
        'Linear additive feature attribution & severity rubric.'
      ]
    },
    {
      role: 'Member 3 — Backend Services & Database',
      name: 'FastAPI & SQLite Systems Engineer',
      items: [
        'FastAPI REST microservice with Pydantic type safety.',
        'Persistent SQLite database schema with indexing.',
        'Batch CSV streaming parser with error validation.',
        'Moderation queue workflows & telemetry calculations.'
      ]
    },
    {
      role: 'Member 4 — Frontend Client & Integration',
      name: 'React UI & Systems Integration',
      items: [
        'Vite + React 19 single-page dashboard with Material UI.',
        'Interactive educational NLP Laboratory diagnostic view.',
        'Recharts visualization suite for telemetry & model weights.',
        'Documentation, verification testing suite & slide outline.'
      ]
    }
  ];

  const specs = [
    { key: 'Dataset', val: 'Jigsaw Toxic Comment Classification Challenge (Kaggle)' },
    { key: 'Total Records', val: '159,571 comments (6 Multi-Label sub-categories)' },
    { key: 'Feature Space', val: 'TF-IDF Unigrams + Bigrams (12,000 max features)' },
    { key: 'Champion Model', val: 'Calibrated Linear Support Vector Machine (Platt Scaling)' },
    { key: 'Validation Macro F1', val: '0.8392 (Balanced class weighting)' },
    { key: 'Inference Latency', val: 'Sub-10 milliseconds per comment (Single-thread CPU)' },
    { key: 'Database', val: 'Local SQLite (Zero-config, zero-cloud dependency)' }
  ];

  return (
    <Box sx={{ p: { xs: 1, md: 2 } }} className="animate-fade-in">
      <Box sx={{ mb: 2.5 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          Project Specifications & Team Deliverables
        </Typography>
        <Typography variant="caption" sx={{ color: 'var(--text-secondary)' }}>
          MCA Major Project technical specifications, 4-member work division, and citations.
        </Typography>
      </Box>

      {/* Specifications Spec-Sheet */}
      <Box className="glass-panel" sx={{ p: 2, mb: 3 }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
          System Technical Specifications
        </Typography>
        <Grid container spacing={1.5}>
          {specs.map((s, idx) => (
            <Grid item xs={12} sm={6} md={4} key={idx}>
              <Box sx={{ p: 1.2, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.7rem' }}>
                  {s.key}
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#e4e4e7', fontSize: '0.82rem', mt: 0.2 }}>
                  {s.val}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Four-Member Deliverable Matrix */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
          Four-Member Technical Deliverables
        </Typography>
        <Grid container spacing={2}>
          {members.map((m, idx) => (
            <Grid item xs={12} sm={6} key={idx}>
              <Box className="glass-panel" sx={{ p: 2, height: '100%' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#818cf8', fontSize: '0.88rem' }}>
                  {m.role}
                </Typography>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', display: 'block', mb: 1.5 }}>
                  {m.name}
                </Typography>
                <Divider sx={{ borderColor: 'var(--border-subtle)', mb: 1.5 }} />
                <Stack spacing={0.8}>
                  {m.items.map((item, i) => (
                    <Typography key={i} variant="caption" sx={{ color: '#d4d4d8', fontSize: '0.76rem', display: 'block' }}>
                      • {item}
                    </Typography>
                  ))}
                </Stack>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Citations */}
      <Box className="glass-panel" sx={{ p: 2 }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1 }}>
          Academic References
        </Typography>
        <Stack spacing={0.8}>
          <Typography variant="caption" sx={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.74rem' }}>
            [1] L. Dixon, J. Li, J. Sorensen, N. Thain, and L. Vasserman, "Measuring and Mitigating Unintended Bias in Text Classification," in <em>Proc. AIES</em>, 2018.
          </Typography>
          <Typography variant="caption" sx={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.74rem' }}>
            [2] D. Borkan, L. Dixon, J. Sorensen, N. Thain, and L. Vasserman, "Nuanced Metrics for Measuring Unintended Bias with Real-world Applications for AI in Social Computing," in <em>Proc. WWW</em>, 2019.
          </Typography>
          <Typography variant="caption" sx={{ color: 'var(--text-secondary)', display: 'block', fontSize: '0.74rem' }}>
            [3] Z. Waseem and D. Hovy, "Hateful Symbols or Hateful People? Predictive Features for Hate Speech Detection," in <em>Proc. NAACL</em>, 2016.
          </Typography>
        </Stack>
      </Box>
    </Box>
  );
}
