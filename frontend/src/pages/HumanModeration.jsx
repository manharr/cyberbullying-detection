import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow,
  Button, Chip, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, CircularProgress, Alert,
  Stack, Select, MenuItem, FormControl, InputLabel,
  IconButton, Tooltip
} from '@mui/material';
import CheckCircleOutlinedIcon from '@mui/icons-material/CheckCircleOutlined';
import DeleteForeverOutlinedIcon from '@mui/icons-material/DeleteForeverOutlined';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import RefreshIcon from '@mui/icons-material/Refresh';
import SeverityBadge from '../components/SeverityBadge';
import { getModerationQueue, updateModerationItem } from '../api/client';

export default function HumanModeration() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('PENDING');

  const [actionItem, setActionItem] = useState(null);
  const [actionType, setActionType] = useState('APPROVED');
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const data = await getModerationQueue(filterStatus);
      setQueue(data);
    } catch (e) {
      setError('Queue offline.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, [filterStatus]);

  const handleOpenAction = (item, type) => {
    setActionItem(item);
    setActionType(type);
    setReviewerNotes('');
    setDialogOpen(true);
  };

  const handleConfirmAction = async () => {
    if (!actionItem) return;
    setActionLoading(true);
    try {
      await updateModerationItem(actionItem.id, actionType, reviewerNotes);
      setDialogOpen(false);
      fetchQueue();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusChip = (status) => {
    switch (status) {
      case 'PENDING':
        return <Chip label="Pending" size="small" sx={{ background: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b', fontWeight: 600, fontSize: '0.7rem', borderRadius: '4px' }} />;
      case 'APPROVED':
        return <Chip label="Approved" size="small" sx={{ background: 'rgba(16, 185, 129, 0.12)', color: '#10b981', fontWeight: 600, fontSize: '0.7rem', borderRadius: '4px' }} />;
      case 'REMOVED':
        return <Chip label="Removed" size="small" sx={{ background: 'rgba(244, 63, 94, 0.12)', color: '#f43f5e', fontWeight: 600, fontSize: '0.7rem', borderRadius: '4px' }} />;
      case 'ESCALATED':
        return <Chip label="Escalated" size="small" sx={{ background: 'rgba(139, 92, 246, 0.12)', color: '#a78bfa', fontWeight: 600, fontSize: '0.7rem', borderRadius: '4px' }} />;
      default:
        return <Chip label={status} size="small" sx={{ fontSize: '0.7rem', borderRadius: '4px' }} />;
    }
  };

  return (
    <Box sx={{ p: { xs: 1, md: 2 } }} className="animate-fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2.5 }}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
            Human Moderation Queue
          </Typography>
          <Typography variant="caption" sx={{ color: 'var(--text-secondary)' }}>
            Review flagged comments requiring manual sign-off or policy action.
          </Typography>
        </Box>

        <Stack direction="row" spacing={1} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel sx={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Filter Status</InputLabel>
            <Select
              value={filterStatus}
              label="Filter Status"
              onChange={(e) => setFilterStatus(e.target.value)}
              sx={{ color: '#fff', fontSize: '0.82rem', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'var(--border-subtle)' } }}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="PENDING">Pending</MenuItem>
              <MenuItem value="APPROVED">Approved</MenuItem>
              <MenuItem value="REMOVED">Removed</MenuItem>
              <MenuItem value="ESCALATED">Escalated</MenuItem>
            </Select>
          </FormControl>

          <Button
            startIcon={<RefreshIcon sx={{ fontSize: 16 }} />}
            variant="outlined"
            onClick={fetchQueue}
            size="small"
            sx={{ borderColor: 'var(--border-subtle)', color: 'var(--text-secondary)' }}
          >
            Refresh
          </Button>
        </Stack>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2, py: 0.5 }}>{error}</Alert>}

      <Box className="glass-panel" sx={{ p: 2 }}>
        {loading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress size={30} sx={{ color: '#818cf8' }} />
          </Box>
        ) : (
          <TableContainer component={Paper} sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ '& th': { color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.74rem', borderColor: 'var(--border-subtle)' } }}>
                  <TableCell width="60">ID</TableCell>
                  <TableCell>Comment</TableCell>
                  <TableCell width="140">Trigger</TableCell>
                  <TableCell width="100">Severity</TableCell>
                  <TableCell width="100">Status</TableCell>
                  <TableCell width="160" align="center">Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {queue.length > 0 ? (
                  queue.map((row) => (
                    <TableRow
                      key={row.id}
                      sx={{ '& td': { color: '#e4e4e7', fontSize: '0.82rem', borderColor: 'var(--border-subtle)' } }}
                    >
                      <TableCell sx={{ color: 'var(--text-muted)' }}>#{row.id}</TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ maxWidth: 350, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: '0.82rem' }}>
                          {row.comment_text}
                        </Typography>
                        {row.reviewer_notes && (
                          <Typography variant="caption" sx={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.7rem' }}>
                            Note: {row.reviewer_notes}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" sx={{ color: '#a1a1aa' }}>
                          {row.flagged_reason}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <SeverityBadge level={row.severity_level} />
                      </TableCell>
                      <TableCell>
                        {getStatusChip(row.status)}
                      </TableCell>
                      <TableCell align="center">
                        {row.status === 'PENDING' ? (
                          <Stack direction="row" spacing={0.5} justifyContent="center">
                            <Button
                              size="small"
                              variant="outlined"
                              color="success"
                              onClick={() => handleOpenAction(row, 'APPROVED')}
                              sx={{ fontSize: '0.68rem', py: 0.2, px: 0.8 }}
                            >
                              Approve
                            </Button>
                            <Button
                              size="small"
                              variant="contained"
                              color="error"
                              onClick={() => handleOpenAction(row, 'REMOVED')}
                              sx={{ fontSize: '0.68rem', py: 0.2, px: 0.8 }}
                            >
                              Remove
                            </Button>
                            <IconButton
                              size="small"
                              onClick={() => handleOpenAction(row, 'ESCALATED')}
                              sx={{ color: '#a78bfa', p: 0.4 }}
                            >
                              <PriorityHighIcon sx={{ fontSize: 16 }} />
                            </IconButton>
                          </Stack>
                        ) : (
                          <Typography variant="caption" sx={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>
                            Resolved
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} sx={{ textAlign: 'center', py: 4, color: 'var(--text-muted)' }}>
                      No items currently in queue.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>

      {/* Confirmation Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        PaperProps={{
          sx: { backgroundColor: '#18181b', color: '#fff', borderRadius: '8px', maxWidth: 440 }
        }}
      >
        <DialogTitle sx={{ fontSize: '1rem', fontWeight: 700 }}>
          Moderation Action: {actionType}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ p: 1.2, borderRadius: '6px', background: 'rgba(0, 0, 0, 0.3)', border: '1px solid var(--border-subtle)', mb: 2 }}>
            <Typography variant="caption" sx={{ color: '#d4d4d8', display: 'block', fontStyle: 'italic' }}>
              "{actionItem?.comment_text}"
            </Typography>
          </Box>
          <TextField
            fullWidth
            size="small"
            label="Review Note"
            value={reviewerNotes}
            onChange={(e) => setReviewerNotes(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: '#fff',
                fontSize: '0.85rem',
                '& fieldset': { borderColor: 'var(--border-subtle)' },
              },
              '& .MuiInputLabel-root': { color: 'var(--text-secondary)', fontSize: '0.85rem' }
            }}
          />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDialogOpen(false)} size="small" sx={{ color: 'var(--text-secondary)' }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            size="small"
            onClick={handleConfirmAction}
            disabled={actionLoading}
            color={actionType === 'APPROVED' ? 'success' : (actionType === 'REMOVED' ? 'error' : 'secondary')}
          >
            {actionLoading ? 'Saving...' : 'Confirm'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
