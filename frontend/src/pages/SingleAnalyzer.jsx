import React, { useState } from 'react';
import {
  Box, Typography, TextField, Button, Grid,
  LinearProgress, Chip, Alert, CircularProgress,
  IconButton, Tooltip, Divider, Stack
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined';
import ThumbDownOutlinedIcon from '@mui/icons-material/ThumbDownOutlined';
import CheckCircleOutlinedIcon from '@mui/icons-material/CheckCircleOutlined';
import ErrorOutlinedIcon from '@mui/icons-material/ErrorOutlined';

import SeverityBadge from '../components/SeverityBadge';
import { analyzeComment, submitFeedback } from '../api/client';

const SAMPLE_PROMPTS = [
  { label: 'Constructive', text: 'Thank you for explaining this concept so clearly! It really helped our group with the assignment.' },
  { label: 'Debate', text: 'I completely disagree with your conclusion, but your citations are well-organized.' },
  { label: 'Insult', text: 'You are an absolute idiot and a complete loser, get out of here.' },
  { label: 'Threat', text: 'I will find you and hurt you, watch your back.' },
  { label: 'Identity Hate', text: 'All people of that religion are evil and disgusting animals.' },
];

export default function SingleAnalyzer() {
  const [commentText, setCommentText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [feedbackSent, setFeedbackSent] = useState(false);

  const handleAnalyze = async () => {
    if (!commentText.trim()) return;
    setLoading(true);
    setError(null);
    setFeedbackSent(false);

    try {
      const data = await analyzeComment(commentText, true);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis service offline.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setCommentText('');
    setResult(null);
    setError(null);
  };

  const handleSendFeedback = async (isAccurate) => {
    if (!result?.id) return;
    try {
      await submitFeedback({
        analysis_id: result.id,
        is_accurate: isAccurate,
        suggested_label: isAccurate ? result.primary_class : (result.is_toxic ? 'Non-toxic' : 'Toxic'),
        user_comments: isAccurate ? 'Accurate' : 'Inaccurate'
      });
      setFeedbackSent(true);
    } catch (e) {
      console.error(e);
    }
  };

  const categoryLabels = {
    toxic: 'Toxic',
    severe_toxic: 'Severe Toxic',
    obscene: 'Obscene',
    threat: 'Threat',
    insult: 'Insult',
    identity_hate: 'Identity Hate'
  };

  return (
    <Box sx={{ p: { xs: 1, md: 2 } }} className="animate-fade-in">
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          Real-Time Comment Analyzer
        </Typography>
        <Typography variant="caption" sx={{ color: 'var(--text-secondary)' }}>
          Input text to trigger toxicity inference, category activation scores, and token attribution.
        </Typography>
      </Box>

      {/* Preset Chips */}
      <Box sx={{ mb: 2, display: 'flex', gap: 0.8, flexWrap: 'wrap', alignItems: 'center' }}>
        <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600, mr: 0.5 }}>
          Presets:
        </Typography>
        {SAMPLE_PROMPTS.map((sample, idx) => (
          <Chip
            key={idx}
            label={sample.label}
            size="small"
            clickable
            onClick={() => setCommentText(sample.text)}
            sx={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
              fontSize: '0.72rem',
              borderRadius: '6px',
              '&:hover': { borderColor: '#818cf8', color: '#fff' }
            }}
          />
        ))}
      </Box>

      {/* Input Panel */}
      <Box className="glass-panel" sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          multiline
          rows={3}
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
          placeholder="Paste comment text to evaluate..."
          variant="outlined"
          sx={{
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'rgba(0, 0, 0, 0.3)',
              color: '#fff',
              fontSize: '0.9rem',
              borderRadius: '8px',
              '& fieldset': { borderColor: 'var(--border-subtle)' },
              '&:hover fieldset': { borderColor: '#3f3f46' },
              '&.Mui-focused fieldset': { borderColor: '#6366f1' },
            },
          }}
        />

        <Box sx={{ mt: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontFamily: 'monospace' }}>
            {commentText.length} / 5000 chars
          </Typography>

          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<DeleteOutlinedIcon sx={{ fontSize: 16 }} />}
              onClick={handleClear}
              disabled={!commentText && !result}
              sx={{ borderColor: 'var(--border-subtle)', color: 'var(--text-secondary)' }}
            >
              Clear
            </Button>
            <Button
              variant="contained"
              size="small"
              endIcon={loading ? <CircularProgress size={14} color="inherit" /> : <SendIcon sx={{ fontSize: 14 }} />}
              onClick={handleAnalyze}
              disabled={loading || !commentText.trim()}
              sx={{ backgroundColor: '#6366f1', px: 2 }}
            >
              {loading ? 'Evaluating...' : 'Analyze'}
            </Button>
          </Stack>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2, py: 0.5, borderRadius: '8px' }}>{error}</Alert>}

      {/* Results View */}
      {result && (
        <Grid container spacing={2} className="animate-fade-in">
          {/* Main Verdict Card */}
          <Grid item xs={12} md={4}>
            <Box className="glass-panel" sx={{ p: 2.5, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
                  Classification
                </Typography>
                <SeverityBadge level={result.severity.level} />
              </Box>

              <Box sx={{ my: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: result.is_toxic ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                    color: result.is_toxic ? '#f43f5e' : '#10b981',
                  }}
                >
                  {result.is_toxic ? <ErrorOutlinedIcon fontSize="small" /> : <CheckCircleOutlinedIcon fontSize="small" />}
                </Box>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: result.is_toxic ? '#f43f5e' : '#10b981', lineHeight: 1.1 }}>
                    {result.primary_class}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'var(--text-secondary)' }}>
                    Confidence: <strong>{(result.confidence * 100).toFixed(1)}%</strong>
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 1.5, borderColor: 'var(--border-subtle)' }} />

              <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600 }}>
                ACTION:
              </Typography>
              <Typography variant="body2" sx={{ color: '#e4e4e7', fontSize: '0.82rem', mt: 0.2 }}>
                {result.severity.recommended_action}
              </Typography>

              {result.severity.factors.length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600 }}>
                    TRIGGERS:
                  </Typography>
                  {result.severity.factors.map((f, i) => (
                    <Typography key={i} variant="caption" sx={{ display: 'block', color: '#a1a1aa', fontSize: '0.74rem', mt: 0.2 }}>
                      • {f}
                    </Typography>
                  ))}
                </Box>
              )}

              {/* Minimalist Feedback */}
              <Box sx={{ mt: 'auto', pt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>
                  Accurate result?
                </Typography>
                {feedbackSent ? (
                  <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 600, fontSize: '0.72rem' }}>
                    ✓ Logged
                  </Typography>
                ) : (
                  <Stack direction="row" spacing={0.5}>
                    <IconButton size="small" onClick={() => handleSendFeedback(true)} sx={{ color: '#10b981', p: 0.4 }}>
                      <ThumbUpOutlinedIcon sx={{ fontSize: 15 }} />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleSendFeedback(false)} sx={{ color: '#f43f5e', p: 0.4 }}>
                      <ThumbDownOutlinedIcon sx={{ fontSize: 15 }} />
                    </IconButton>
                  </Stack>
                )}
              </Box>
            </Box>
          </Grid>

          {/* Category Scores & Tokens */}
          <Grid item xs={12} md={8}>
            <Stack spacing={2}>
              {/* Category Breakdown */}
              <Box className="glass-panel" sx={{ p: 2 }}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1.5 }}>
                  Category Activations
                </Typography>
                <Grid container spacing={1.5}>
                  {Object.entries(result.category_scores || {}).map(([key, score]) => {
                    const pct = Math.round(score * 100);
                    const isFlagged = pct >= 40;
                    return (
                      <Grid item xs={6} sm={4} key={key}>
                        <Box sx={{ p: 1, borderRadius: '6px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-subtle)' }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography variant="caption" sx={{ fontWeight: 600, color: isFlagged ? '#f43f5e' : '#d4d4d8', fontSize: '0.75rem' }}>
                              {categoryLabels[key] || key}
                            </Typography>
                            <Typography variant="caption" sx={{ fontWeight: 700, color: isFlagged ? '#f43f5e' : 'var(--text-muted)', fontSize: '0.72rem' }}>
                              {pct}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={pct}
                            sx={{
                              height: 4,
                              borderRadius: 2,
                              backgroundColor: 'rgba(255, 255, 255, 0.04)',
                              '& .MuiLinearProgress-bar': {
                                backgroundColor: isFlagged ? '#f43f5e' : '#6366f1',
                              }
                            }}
                          />
                        </Box>
                      </Grid>
                    );
                  })}
                </Grid>
              </Box>

              {/* Influential Terms */}
              <Box className="glass-panel" sx={{ p: 2 }}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', display: 'block', mb: 1 }}>
                  Influential Terms & Additive Weights
                </Typography>
                {result.influential_words && result.influential_words.length > 0 ? (
                  <Box sx={{ display: 'flex', gap: 0.8, flexWrap: 'wrap' }}>
                    {result.influential_words.map((item, idx) => (
                      <Chip
                        key={idx}
                        label={`${item.word} (${item.contribution > 0 ? '+' : ''}${item.contribution})`}
                        size="small"
                        className={item.polarity === 'toxic' ? 'polarity-toxic' : 'polarity-safe'}
                        sx={{ fontSize: '0.72rem', borderRadius: '4px', fontFamily: 'monospace' }}
                      />
                    ))}
                  </Box>
                ) : (
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>
                    No dictionary vocabulary triggers found in this comment.
                  </Typography>
                )}
              </Box>
            </Stack>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
