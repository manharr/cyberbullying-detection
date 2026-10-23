import React, { useState, useEffect } from 'react';
import {
  Box, Typography, TextField, Select, MenuItem,
  FormControl, InputLabel, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, TablePagination,
  Paper, IconButton, Tooltip, Dialog, DialogTitle,
  DialogContent, DialogActions, Button, Chip, CircularProgress,
  Alert, Stack, Divider, Grid
} from '@mui/material';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import SeverityBadge from '../components/SeverityBadge';
import { getHistory, getHistoryById, deleteHistoryItem } from '../api/client';

export default function AnalysisHistory() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [filterToxic, setFilterToxic] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('');

  // Selected item modal
  const [selectedItem, setSelectedItem] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);

  // Delete confirm dialog
  const [deleteId, setDeleteId] = useState(null);

  const fetchHistoryData = async () => {
    setLoading(true);
    try {
      const params = {
        limit: rowsPerPage,
        offset: page * rowsPerPage,
      };
      if (filterToxic !== '') params.is_toxic = filterToxic === 'true';
      if (filterSeverity !== '') params.severity = parseInt(filterSeverity, 10);
      if (searchTerm.trim()) params.search = searchTerm.trim();

      const data = await getHistory(params);
      setItems(data.items || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistoryData();
  }, [page, rowsPerPage, filterToxic, filterSeverity]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(0);
    fetchHistoryData();
  };

  const handleOpenDetails = async (id) => {
    setModalLoading(true);
    setModalOpen(true);
    try {
      const data = await getHistoryById(id);
      setSelectedItem(data);
    } catch (e) {
      console.error(e);
    } finally {
      setModalLoading(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteHistoryItem(deleteId);
      setDeleteId(null);
      fetchHistoryData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }} className="animate-fade-in">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 800, letterSpacing: '-0.02em' }}>
          Analysis History & Persistence
        </Typography>
        <Typography variant="body2" sx={{ color: 'var(--text-secondary)' }}>
          Browse, inspect, filter, and manage historical predictions preserved in local SQLite storage.
        </Typography>
      </Box>

      {/* Filter and Search Bar */}
      <Box className="glass-panel" sx={{ p: 2.5, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={5}>
            <form onSubmit={handleSearch}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search comment contents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ color: 'var(--text-muted)', mr: 1, fontSize: 20 }} />,
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: '#fff',
                    '& fieldset': { borderColor: 'var(--border-subtle)' },
                    '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.2)' },
                  }
                }}
              />
            </form>
          </Grid>

          <Grid item xs={6} sm={3}>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: 'var(--text-secondary)' }}>Toxicity Filter</InputLabel>
              <Select
                value={filterToxic}
                label="Toxicity Filter"
                onChange={(e) => { setFilterToxic(e.target.value); setPage(0); }}
                sx={{
                  color: '#fff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'var(--border-subtle)' },
                }}
              >
                <MenuItem value="">All Classifications</MenuItem>
                <MenuItem value="true">Toxic Only</MenuItem>
                <MenuItem value="false">Non-toxic Only</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={6} sm={3}>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: 'var(--text-secondary)' }}>Severity Filter</InputLabel>
              <Select
                value={filterSeverity}
                label="Severity Filter"
                onChange={(e) => { setFilterSeverity(e.target.value); setPage(0); }}
                sx={{
                  color: '#fff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: 'var(--border-subtle)' },
                }}
              >
                <MenuItem value="">All Severities</MenuItem>
                <MenuItem value="0">Level 0 (None)</MenuItem>
                <MenuItem value="1">Level 1 (Low)</MenuItem>
                <MenuItem value="2">Level 2 (Moderate)</MenuItem>
                <MenuItem value="3">Level 3 (High)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={1}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
              sx={{ backgroundColor: '#6366F1', minWidth: 'auto', px: 2 }}
            >
              Filter
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* History Table */}
      <Box className="glass-panel" sx={{ p: 2 }}>
        {loading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress size={30} sx={{ color: '#818CF8' }} />
          </Box>
        ) : (
          <>
            <TableContainer component={Paper} sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ '& th': { color: 'var(--text-secondary)', fontWeight: 700, borderColor: 'var(--border-subtle)' } }}>
                    <TableCell width="60">ID</TableCell>
                    <TableCell>Comment Text Excerpt</TableCell>
                    <TableCell width="120">Classification</TableCell>
                    <TableCell width="130">Severity</TableCell>
                    <TableCell width="100">Confidence</TableCell>
                    <TableCell width="140">Date</TableCell>
                    <TableCell width="90" align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {items.length > 0 ? (
                    items.map((row) => (
                      <TableRow
                        key={row.id}
                        sx={{
                          '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.02)' },
                          '& td': { color: '#E2E8F0', borderColor: 'var(--border-subtle)' }
                        }}
                      >
                        <TableCell sx={{ color: 'var(--text-muted)' }}>#{row.id}</TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ maxWidth: 380, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {row.comment_text}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={row.is_toxic ? 'Toxic' : 'Non-toxic'}
                            size="small"
                            sx={{
                              backgroundColor: row.is_toxic ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                              color: row.is_toxic ? '#F43F5E' : '#10B981',
                              fontWeight: 600,
                              fontSize: '0.72rem'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <SeverityBadge level={row.estimated_severity} size="small" />
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" sx={{ fontWeight: 600 }}>
                            {(row.confidence * 100).toFixed(1)}%
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>
                            {new Date(row.created_at).toLocaleDateString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Stack direction="row" spacing={0.5} justifyContent="center">
                            <Tooltip title="View Full Inspection">
                              <IconButton size="small" onClick={() => handleOpenDetails(row.id)} sx={{ color: '#818CF8' }}>
                                <VisibilityOutlinedIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete Record">
                              <IconButton size="small" onClick={() => setDeleteId(row.id)} sx={{ color: '#F43F5E' }}>
                                <DeleteOutlinedIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={7} sx={{ textAlign: 'center', py: 4, color: 'var(--text-muted)' }}>
                        No analysis records matching your criteria.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              rowsPerPageOptions={[5, 10, 25, 50]}
              component="div"
              count={total}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={(e, p) => setPage(p)}
              onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
              sx={{ color: 'var(--text-secondary)', borderTop: '1px solid var(--border-subtle)', mt: 1 }}
            />
          </>
        )}
      </Box>

      {/* Details Dialog */}
      <Dialog
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#111827',
            color: '#fff',
            border: '1px solid var(--border-subtle)',
            borderRadius: 3
          }
        }}
      >
        <DialogTitle sx={{ borderBottom: '1px solid var(--border-subtle)' }}>
          Analysis Record #{selectedItem?.id}
        </DialogTitle>
        <DialogContent sx={{ mt: 2 }}>
          {modalLoading || !selectedItem ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <CircularProgress size={30} sx={{ color: '#818CF8' }} />
            </Box>
          ) : (
            <Stack spacing={2.5}>
              <Box>
                <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600 }}>
                  RAW COMMENT TEXT:
                </Typography>
                <Box sx={{ p: 2, borderRadius: 2, background: 'rgba(0, 0, 0, 0.3)', mt: 0.5 }}>
                  <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                    {selectedItem.comment_text}
                  </Typography>
                </Box>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>Classification:</Typography>
                  <Typography variant="h6" sx={{ color: selectedItem.is_toxic ? '#F43F5E' : '#10B981', fontWeight: 800 }}>
                    {selectedItem.primary_class} ({(selectedItem.confidence * 100).toFixed(1)}%)
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)' }}>Severity Level:</Typography>
                  <Box sx={{ mt: 0.5 }}>
                    <SeverityBadge level={selectedItem.estimated_severity} />
                  </Box>
                </Grid>
              </Grid>

              {/* Influential Words */}
              {selectedItem.influential_words && selectedItem.influential_words.length > 0 && (
                <Box>
                  <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontWeight: 600, display: 'block', mb: 1 }}>
                    INFLUENTIAL WORDS:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {selectedItem.influential_words.map((w, idx) => (
                      <Chip
                        key={idx}
                        label={`${w.word} (${w.contribution > 0 ? '+' : ''}${w.contribution})`}
                        size="small"
                        className={w.polarity === 'toxic' ? 'polarity-toxic' : 'polarity-safe'}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2, borderTop: '1px solid var(--border-subtle)' }}>
          <Button onClick={() => setModalOpen(false)} sx={{ color: 'var(--text-secondary)' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={Boolean(deleteId)}
        onClose={() => setDeleteId(null)}
        PaperProps={{
          sx: { backgroundColor: '#1E293B', color: '#fff', borderRadius: 2 }
        }}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ color: 'var(--text-secondary)' }}>
            Are you sure you want to delete analysis record #{deleteId}? This action permanently deletes this record and any linked moderation item.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDeleteId(null)} sx={{ color: 'var(--text-secondary)' }}>
            Cancel
          </Button>
          <Button onClick={handleConfirmDelete} variant="contained" color="error">
            Delete Record
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
