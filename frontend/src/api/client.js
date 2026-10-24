import axios from 'axios';

const api = axios.create({
  baseURL: '', // Uses Vite proxy
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkHealth = () => api.get('/health').then(r => r.data);

export const analyzeComment = (commentText, autoSave = true, model = 'linear_svm', threshold = null) => {
  const payload = { comment_text: commentText, auto_save: autoSave, model };
  if (threshold !== null && threshold !== undefined) {
    payload.threshold = threshold;
  }
  return api.post('/api/analyze', payload).then(r => r.data);
};

export const getThresholdTuning = () =>
  api.get('/api/model/threshold-tuning').then(r => r.data);

export const analyzeBatchCSV = (formData, textColumn = 'comment_text') =>
  api.post(`/api/analyze/batch?text_column=${encodeURIComponent(textColumn)}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data);

export const getHistory = (params = {}) =>
  api.get('/api/history', { params }).then(r => r.data);

export const getHistoryById = (id) =>
  api.get(`/api/history/${id}`).then(r => r.data);

export const deleteHistoryItem = (id) =>
  api.delete(`/api/history/${id}`).then(r => r.data);

export const getDashboardStats = () =>
  api.get('/api/dashboard/stats').then(r => r.data);

export const getModelMetrics = () =>
  api.get('/api/model/metrics').then(r => r.data);

export const getModelComparison = () =>
  api.get('/api/model/comparison').then(r => r.data);

export const getGlobalExplanations = (topN = 25) =>
  api.get(`/api/explain/global?top_n=${topN}`).then(r => r.data);

export const inspectNlpLab = (text) =>
  api.post('/api/nlp/laboratory', { text }).then(r => r.data);

export const getErrorAnalysis = () =>
  api.get('/api/evaluation/errors').then(r => r.data);

export const getFairnessAnalysis = () =>
  api.get('/api/evaluation/fairness').then(r => r.data);

export const getModerationQueue = (status = '') =>
  api.get('/api/moderation/queue', { params: status ? { status } : {} }).then(r => r.data);

export const updateModerationItem = (id, status, reviewerNotes = '') =>
  api.patch(`/api/moderation/${id}`, { status, reviewer_notes: reviewerNotes }).then(r => r.data);

export const submitFeedback = (payload) =>
  api.post('/api/feedback', payload).then(r => r.data);

export default api;
