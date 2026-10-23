import React, { useState } from 'react';
import {
  Box, Typography, Button, TextField, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, TablePagination,
  Paper, CircularProgress, Alert, Chip, Stack, Grid
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DownloadIcon from '@mui/icons-material/Download';
import CheckCircleOutlinedIcon from '@mui/icons-material/CheckCircleOutlined';
import ReportProblemOutlinedIcon from '@mui/icons-material/ReportProblemOutlined';
import SeverityBadge from '../components/SeverityBadge';
import { analyzeBatchCSV } from '../api/client';

export default function BatchAnalysis() {
  const [file, setFile] = useState(null);
  const [columnName, setColumnName] = useState('comment_text');
  const [loading, setLoading] = useState(false);
  const [batchResult, setBatchResult] = useState(null);
  const [error, setError] = useState(null);

  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleProcessBatch = async () => {
    if (!file) {
      setError('Please select a CSV file first.');
      return;
    }
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const data = await analyzeBatchCSV(formData, columnName);
      setBatchResult(data);
      setPage(0);
    } catch (err) {
      setError(err.response?.data?.detail || 'Batch processing failed. Verify CSV structure.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCSV = () => {
    if (!batchResult || !batchResult.results.length) return;

    const headers = ['Row', 'Comment Text', 'Prediction', 'Confidence', 'Severity Level', 'Severity Label'];
    const rows = batchResult.results.map(r => [
      r.row_index,
      `"${r.comment_text.replace(/"/g, '""')}"`,
      r.is_toxic ? 'Toxic' : 'Non-toxic',
      r.confidence,
      r.estimated_severity,
      r.severity_label
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map(e => e.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `classified_batch_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }} className="animate-fade-in">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 800, letterSpacing: '-0.02em' }}>
          Batch CSV Analysis
        </Typography>
        <Typography variant="body2" sx={{ color: 'var(--text-secondary)' }}>
          Upload a CSV spreadsheet containing user comments to run high-throughput batch classification and severity scoring.
        </Typography>
      </Box>

      {/* Upload Box */}
      <Box className="glass-panel" sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <Box
              sx={{
                p: 3,
                border: '2px dashed var(--border-subtle)',
                borderRadius: 2,
                textAlign: 'center',
                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                cursor: 'pointer',
                transition: 'border-color 0.2s ease',
                '&:hover': { borderColor: '#818CF8' }
              }}
              component="label"
            >
              <input
                type="file"
                accept=".csv"
                hidden
                onChange={handleFileChange}
              />
              <CloudUploadIcon sx={{ fontSize: 38, color: '#818CF8', mb: 1 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                {file ? file.name : 'Click to select or drop CSV file'}
              </Typography>
              <Typography variant="caption" sx={{ color: 'var(--text-muted)', display: 'block' }}>
                Supports standard comma-separated text files (max 1000 rows per batch)
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Stack spacing={2}>
              <TextField
                label="Target Text Column Name"
                variant="outlined"
                size="small"
                value={columnName}
                onChange={(e) => setColumnName(e.target.value)}
                helperText="Column containing comment strings (e.g., 'comment_text', 'text', 'comment')"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: '#fff',
                    '& fieldset': { borderColor: 'var(--border-subtle)' },
                    '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                  },
                  '& .MuiInputLabel-root': { color: 'var(--text-secondary)' },
                  '& .MuiFormHelperText-root': { color: 'var(--text-muted)' }
                }}
              />

              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <CloudUploadIcon />}
                onClick={handleProcessBatch}
                disabled={loading || !file}
                sx={{
                  backgroundColor: '#6366F1',
                  fontWeight: 700,
                  py: 1.2,
                  borderRadius: 2,
                  '&:hover': { backgroundColor: '#4F46E5' }
                }}
              >
                {loading ? 'Processing Batch...' : 'Process Batch Records'}
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Batch Summary & Table */}
      {batchResult && (
        <Box className="animate-fade-in">
          {/* Summary Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={4}>
              <Box className="glass-panel" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600 }}>
                  TOTAL PROCESSED
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 800, mt: 0.5 }}>
                  {batchResult.total_processed}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box className="glass-panel" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="caption" sx={{ color: '#F43F5E', fontWeight: 600 }}>
                  TOXIC / HARASSMENT DETECTED
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 800, mt: 0.5, color: '#F43F5E' }}>
                  {batchResult.total_toxic}
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)', ml: 1 }}>
                    ({((batchResult.total_toxic / batchResult.total_processed) * 100).toFixed(1)}%)
                  </Typography>
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box className="glass-panel" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="caption" sx={{ color: '#10B981', fontWeight: 600 }}>
                  NON-TOXIC / CLEAN
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 800, mt: 0.5, color: '#10B981' }}>
                  {batchResult.total_non_toxic}
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)', ml: 1 }}>
                    ({((batchResult.total_non_toxic / batchResult.total_processed) * 100).toFixed(1)}%)
                  </Typography>
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Table Container */}
          <Box className="glass-panel" sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, px: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                Classified Batch Records
              </Typography>
              <Button
                variant="outlined"
                size="small"
                startIcon={<DownloadIcon />}
                onClick={handleDownloadCSV}
                sx={{
                  borderColor: 'var(--border-subtle)',
                  color: '#fff',
                  borderRadius: 2,
                  '&:hover': { borderColor: '#818CF8', backgroundColor: 'rgba(99, 102, 241, 0.1)' }
                }}
              >
                Download CSV
              </Button>
            </Box>

            <TableContainer component={Paper} sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ '& th': { color: 'var(--text-secondary)', fontWeight: 700, borderColor: 'var(--border-subtle)' } }}>
                    <TableCell width="60">#</TableCell>
                    <TableCell>Comment Text Excerpt</TableCell>
                    <TableCell width="120">Classification</TableCell>
                    <TableCell width="120">Severity</TableCell>
                    <TableCell width="100">Confidence</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {batchResult.results
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((row) => (
                      <TableRow
                        key={row.row_index}
                        sx={{
                          '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.02)' },
                          '& td': { color: '#E2E8F0', borderColor: 'var(--border-subtle)' }
                        }}
                      >
                        <TableCell sx={{ color: 'var(--text-muted)' }}>{row.row_index}</TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ maxWidth: 450, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {row.comment_text}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={row.is_toxic ? <ReportProblemOutlinedIcon sx={{ fontSize: 14 }} /> : <CheckCircleOutlinedIcon sx={{ fontSize: 14 }} />}
                            label={row.is_toxic ? 'Toxic' : 'Non-toxic'}
                            size="small"
                            sx={{
                              backgroundColor: row.is_toxic ? 'rgba(244, 63, 94, 0.12)' : 'rgba(16, 185, 129, 0.12)',
                              color: row.is_toxic ? '#F43F5E' : '#10B981',
                              border: `1px solid ${row.is_toxic ? 'rgba(244, 63, 94, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
                              fontWeight: 600,
                              fontSize: '0.72rem'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <SeverityBadge level={row.estimated_severity} size="small" />
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" sx={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
                            {(row.confidence * 100).toFixed(1)}%
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              rowsPerPageOptions={[5, 10, 25, 50]}
              component="div"
              count={batchResult.results.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              sx={{
                color: 'var(--text-secondary)',
                borderTop: '1px solid var(--border-subtle)',
                mt: 1
              }}
            />
          </Box>
        </Box>
      )}
    </Box>
  );
}
