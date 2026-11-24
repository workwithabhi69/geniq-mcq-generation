import type { HealthStatus, GenerationRequest, GenerationResponse, ExperimentSummary } from '../types';

const API_BASE = 'http://127.0.0.1:8000/api';

export const api = {
  async getHealth(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
  },

  async setApiKey(apiKey: string) {
    const res = await fetch(`${API_BASE}/config/key`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to set API key');
    }
    return res.json();
  },

  async uploadPdf(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'PDF upload failed');
    }
    return res.json();
  },

  async generateMCQs(payload: GenerationRequest): Promise<GenerationResponse> {
    const res = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'MCQ generation failed');
    }
    return res.json();
  },

  async getQuestions(filters?: { topic?: string; difficulty?: string; model?: string }): Promise<any[]> {
    const params = new URLSearchParams();
    if (filters?.topic) params.append('topic', filters.topic);
    if (filters?.difficulty) params.append('difficulty', filters.difficulty);
    if (filters?.model) params.append('model', filters.model);

    const res = await fetch(`${API_BASE}/questions?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch questions');
    return res.json();
  },

  async deleteQuestion(id: number) {
    const res = await fetch(`${API_BASE}/questions/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete question');
    return res.json();
  },

  async clearAllQuestions() {
    const res = await fetch(`${API_BASE}/questions`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to clear questions');
    return res.json();
  },

  async getExperiments(): Promise<Record<string, { summary: ExperimentSummary; config: any }>> {
    const res = await fetch(`${API_BASE}/experiments`);
    if (!res.ok) throw new Error('Failed to fetch experiments');
    return res.json();
  },

  async runExperiment(expId: string, sampleSize: number = 5): Promise<ExperimentSummary> {
    const res = await fetch(`${API_BASE}/experiments/run?exp_id=${expId}&sample_size=${sampleSize}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Experiment run failed');
    }
    return res.json();
  },

  async getAnalytics() {
    const res = await fetch(`${API_BASE}/analytics`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  }
};
