import React from 'react';
import {
  Box, Typography, Grid, Card, CardActionArea, Button, Stack
} from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import EditNoteOutlinedIcon from '@mui/icons-material/EditNoteOutlined';
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined';
import ScienceOutlinedIcon from '@mui/icons-material/ScienceOutlined';
import TuneOutlinedIcon from '@mui/icons-material/TuneOutlined';
import BarChartOutlinedIcon from '@mui/icons-material/BarChartOutlined';
import PsychologyOutlinedIcon from '@mui/icons-material/PsychologyOutlined';

export default function Overview({ onNavigate }) {
  const kpis = [
    { label: 'Dataset Records', value: '159.5k', sub: 'Jigsaw Challenge' },
    { label: 'Champion Classifier', value: 'Linear SVM', sub: 'Calibrated Platt Scaling' },
    { label: 'Validation Macro F1', value: '0.8392', sub: 'Balanced Weighting' },
    { label: 'Inference Latency', value: '< 10 ms', sub: 'Single-thread CPU' },
  ];

  const modules = [
    { id: 'single', title: 'Single Analyzer', desc: 'Real-time comment classification, 6-category scoring & token attribution.', icon: <EditNoteOutlinedIcon sx={{ color: '#818cf8' }} /> },
    { id: 'batch', title: 'Batch Processing', desc: 'Upload CSV datasets, batch-score rows, and export predictions.', icon: <CloudUploadOutlinedIcon sx={{ color: '#06b6d4' }} /> },
    { id: 'lab', title: 'NLP Laboratory', desc: 'Inspect discrete stages: Cleaning, Tokenization, Stopwords, Lemmas, TF-IDF.', icon: <ScienceOutlinedIcon sx={{ color: '#10b981' }} /> },
    { id: 'comparison', title: 'Model Benchmarks', desc: 'Compare Linear SVM, Logistic Regression, and Naive Bayes on held-out tests.', icon: <TuneOutlinedIcon sx={{ color: '#f59e0b' }} /> },
    { id: 'dashboard', title: 'Analytics Telemetry', desc: 'Real-time SQLite metrics, severity histograms, and category breakdown.', icon: <BarChartOutlinedIcon sx={{ color: '#ec4899' }} /> },
    { id: 'explain', title: 'Explainability (XAI)', desc: 'Inspect learned linear feature weights and additive token contributions.', icon: <PsychologyOutlinedIcon sx={{ color: '#a78bfa' }} /> },
  ];

  const pipelineStages = [
    { num: '01', name: 'Text Cleaning', desc: 'HTML & noise sanitization' },
    { num: '02', name: 'Tokenization', desc: 'NLTK lexical boundary parsing' },
    { num: '03', name: 'Negation Stopwords', desc: 'Protects "not", "no", "never"' },
    { num: '04', name: 'Lemmatization', desc: 'WordNet morphological bases' },
    { num: '05', name: 'TF-IDF Vectors', desc: 'Unigram + Bigram feature matrix' },
    { num: '06', name: 'SVM Inference', desc: 'Multi-label & severity triage' },
  ];

  return (
    <Box sx={{ p: { xs: 1, md: 2 } }} className="animate-fade-in">
      {/* Top Banner */}
      <Box
        className="glass-panel"
        sx={{
          p: { xs: 2.5, md: 3 },
          mb: 3,
          background: 'linear-gradient(180deg, #131318 0%, #0e0e12 100%)',
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, letterSpacing: '-0.02em', mb: 0.5 }}>
              Cyberbullying Detection & Severity Engine
            </Typography>
            <Typography variant="body2" sx={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Advanced NLP classification system built on Kaggle Jigsaw data with explainable feature attribution.
            </Typography>
          </Box>
          <Stack direction="row" spacing={1.5}>
            <Button
              variant="contained"
              size="small"
              endIcon={<ArrowForwardIcon sx={{ fontSize: 16 }} />}
              onClick={() => onNavigate('single')}
              sx={{ backgroundColor: '#6366f1', px: 2, py: 0.8 }}
            >
              Open Analyzer
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={() => onNavigate('lab')}
              sx={{ borderColor: 'var(--border-subtle)', color: 'var(--text-secondary)' }}
            >
              NLP Lab
            </Button>
          </Stack>
        </Box>

        {/* KPI Strip */}
        <Grid container spacing={2} sx={{ mt: 2 }}>
          {kpis.map((k, i) => (
            <Grid item xs={6} md={3} key={i}>
              <Box sx={{ p: 1.5, borderRadius: '8px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600, display: 'block', textTransform: 'uppercase', fontSize: '0.68rem' }}>
                  {k.label}
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 700, mt: 0.2, color: '#fff' }}>
                  {k.value}
                </Typography>
                <Typography variant="caption" sx={{ color: 'var(--text-secondary)', fontSize: '0.72rem' }}>
                  {k.sub}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* NLP Pipeline Strip */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
          Pipeline Architecture
        </Typography>
        <Grid container spacing={1.5}>
          {pipelineStages.map((stage, idx) => (
            <Grid item xs={6} sm={4} md={2} key={idx}>
              <Box className="glass-panel" sx={{ p: 1.5, height: '100%' }}>
                <Typography variant="caption" sx={{ color: '#818cf8', fontWeight: 700, fontFamily: 'monospace' }}>
                  {stage.num}
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, mt: 0.3, color: '#e4e4e7', fontSize: '0.82rem' }}>
                  {stage.name}
                </Typography>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', display: 'block', mt: 0.2, fontSize: '0.7rem' }}>
                  {stage.desc}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Modules Grid */}
      <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
        Core Modules
      </Typography>
      <Grid container spacing={2}>
        {modules.map((m) => (
          <Grid item xs={12} sm={6} md={4} key={m.id}>
            <Card className="glass-panel" sx={{ height: '100%' }}>
              <CardActionArea onClick={() => onNavigate(m.id)} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <Box sx={{ p: 0.8, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)', mb: 1.2 }}>
                  {m.icon}
                </Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#f4f4f5', mb: 0.4 }}>
                  {m.title}
                </Typography>
                <Typography variant="caption" sx={{ color: 'var(--text-secondary)', lineHeight: 1.4, fontSize: '0.78rem' }}>
                  {m.desc}
                </Typography>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
