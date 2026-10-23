import React, { useState, useEffect } from 'react';
import {
  Box, Typography, TextField, Button, Grid,
  Chip, CircularProgress, Alert, Stack
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { inspectNlpLab } from '../api/client';

const SAMPLES = [
  { label: 'Negation Retention', text: 'I am not going to attack you, but bullies were attacking!' },
  { label: 'Lemmas vs Stems', text: 'The bullies are running quickly and connections were connecting better!' },
  { label: 'Sanitization Noise', text: '<b>Hello</b> @user_99 visit https://example.com for answers!' },
  { label: 'Abuse Lexicon', text: 'You are completely useless, stupid, and nobody wants you.' }
];

export default function NlpLaboratory() {
  const [inputText, setInputText] = useState(SAMPLES[0].text);
  const [labData, setLabData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInspect = async (textToUse = inputText) => {
    if (!textToUse.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await inspectNlpLab(textToUse);
      setLabData(data);
    } catch (err) {
      setError('Inspection failed.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleInspect(SAMPLES[0].text);
  }, []);

  return (
    <Box sx={{ p: { xs: 1, md: 2 } }} className="animate-fade-in">
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          Educational NLP Pipeline Inspector
        </Typography>
        <Typography variant="caption" sx={{ color: 'var(--text-secondary)' }}>
          Step-by-step diagnostic breakdown across all sequential text transformation stages.
        </Typography>
      </Box>

      {/* Preset Chips */}
      <Box sx={{ mb: 1.5, display: 'flex', gap: 0.8, flexWrap: 'wrap', alignItems: 'center' }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600 }}>
          Scenarios:
        </Typography>
        {SAMPLES.map((s, idx) => (
          <Chip
            key={idx}
            label={s.label}
            size="small"
            clickable
            onClick={() => {
              setInputText(s.text);
              handleInspect(s.text);
            }}
            sx={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
              fontSize: '0.72rem',
              borderRadius: '6px',
              '&:hover': { borderColor: '#10b981', color: '#fff' }
            }}
          />
        ))}
      </Box>

      {/* Input */}
      <Box className="glass-panel" sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          size="small"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Enter sentence..."
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
        <Box sx={{ mt: 1.5, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            size="small"
            startIcon={loading ? <CircularProgress size={14} color="inherit" /> : <PlayArrowIcon sx={{ fontSize: 16 }} />}
            onClick={() => handleInspect(inputText)}
            disabled={loading || !inputText.trim()}
            sx={{ backgroundColor: '#10b981', px: 2 }}
          >
            {loading ? 'Inspecting...' : 'Run Pipeline'}
          </Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2, py: 0.5 }}>{error}</Alert>}

      {/* Step Inspector View */}
      {labData && (
        <Stack spacing={2} className="animate-fade-in">
          {/* Stage A */}
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#818cf8', fontWeight: 700, textTransform: 'uppercase' }}>
              Stage A — Sanitization & Cleaning
            </Typography>
            <Grid container spacing={1.5} sx={{ mt: 0.5 }}>
              <Grid item xs={12} md={6}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>RAW:</Typography>
                <Box sx={{ p: 1, borderRadius: '6px', background: 'rgba(0, 0, 0, 0.3)', border: '1px solid var(--border-subtle)', mt: 0.3 }}>
                  <Typography variant="caption" sx={{ fontFamily: 'monospace', color: '#f87171', display: 'block' }}>
                    {labData.stage_a_raw}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>CLEANED:</Typography>
                <Box sx={{ p: 1, borderRadius: '6px', background: 'rgba(0, 0, 0, 0.3)', border: '1px solid var(--border-subtle)', mt: 0.3 }}>
                  <Typography variant="caption" sx={{ fontFamily: 'monospace', color: '#34d399', display: 'block' }}>
                    {labData.stage_a_cleaned || '<Empty>'}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>

          {/* Stage B */}
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="caption" sx={{ color: '#06b6d4', fontWeight: 700, textTransform: 'uppercase' }}>
                Stage B — Tokenization
              </Typography>
              <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                {labData.stage_b_token_count} tokens
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 0.6, flexWrap: 'wrap' }}>
              {labData.stage_b_tokens.map((tok, i) => (
                <Chip
                  key={i}
                  label={tok}
                  size="small"
                  sx={{
                    fontFamily: 'monospace',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--border-subtle)',
                    color: '#e4e4e7',
                    borderRadius: '4px',
                    fontSize: '0.72rem'
                  }}
                />
              ))}
            </Box>
          </Box>

          {/* Stage C */}
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#f59e0b', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1 }}>
              Stage C — Stop-Words & Negation Handling
            </Typography>
            <Grid container spacing={1.5}>
              <Grid item xs={12} sm={6}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>Pruned Stopwords:</Typography>
                <Box sx={{ display: 'flex', gap: 0.6, flexWrap: 'wrap', mt: 0.5 }}>
                  {labData.stage_c_removed_stopwords.length > 0 ? (
                    labData.stage_c_removed_stopwords.map((sw, i) => (
                      <Chip key={i} label={sw} size="small" sx={{ background: 'rgba(255, 255, 255, 0.03)', color: 'var(--text-muted)', fontSize: '0.7rem', borderRadius: '4px' }} />
                    ))
                  ) : (
                    <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>None</Typography>
                  )}
                </Box>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 600 }}>Protected Negations:</Typography>
                <Box sx={{ display: 'flex', gap: 0.6, flexWrap: 'wrap', mt: 0.5 }}>
                  {labData.stage_c_preserved_negations.length > 0 ? (
                    labData.stage_c_preserved_negations.map((neg, i) => (
                      <Chip key={i} label={neg} size="small" sx={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', fontWeight: 700, fontSize: '0.7rem', borderRadius: '4px' }} />
                    ))
                  ) : (
                    <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>No negation words</Typography>
                  )}
                </Box>
              </Grid>
            </Grid>
          </Box>

          {/* Stage D & E */}
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 0.8 }}>
                  Stage D — WordNet Lemmatization
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.6, flexWrap: 'wrap' }}>
                  {labData.stage_d_lemmatized.map((l, i) => (
                    <Chip key={i} label={l} size="small" sx={{ background: 'rgba(16, 185, 129, 0.08)', color: '#6ee7b7', fontFamily: 'monospace', borderRadius: '4px', fontSize: '0.72rem' }} />
                  ))}
                </Box>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="caption" sx={{ color: '#ec4899', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 0.8 }}>
                  Stage E — Porter Stemming
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.6, flexWrap: 'wrap' }}>
                  {labData.stage_e_stemmed.map((s, i) => (
                    <Chip key={i} label={s} size="small" sx={{ background: 'rgba(236, 72, 153, 0.08)', color: '#f472b6', fontFamily: 'monospace', borderRadius: '4px', fontSize: '0.72rem' }} />
                  ))}
                </Box>
              </Grid>
            </Grid>
          </Box>

          {/* Stage F */}
          <Box className="glass-panel" sx={{ p: 2 }}>
            <Typography variant="caption" sx={{ color: '#818cf8', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1 }}>
              Stage F — Active TF-IDF Vectors
            </Typography>
            <Box sx={{ display: 'flex', gap: 0.8, flexWrap: 'wrap' }}>
              {labData.tfidf_active_terms && labData.tfidf_active_terms.length > 0 ? (
                labData.tfidf_active_terms.map((t, i) => (
                  <Chip
                    key={i}
                    label={`${t.term} : ${t.tfidf_weight}`}
                    size="small"
                    sx={{
                      fontFamily: 'monospace',
                      background: 'rgba(99, 102, 241, 0.1)',
                      border: '1px solid rgba(99, 102, 241, 0.25)',
                      color: '#c7d2fe',
                      borderRadius: '4px',
                      fontSize: '0.72rem'
                    }}
                  />
                ))
              ) : (
                <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>
                  No vocabulary matches.
                </Typography>
              )}
            </Box>
          </Box>
        </Stack>
      )}
    </Box>
  );
}
