export interface MCQOptions {
  A: string;
  B: string;
  C: string;
  D: string;
}

export interface MCQOutput {
  id?: number;
  question: string;
  options: MCQOptions;
  correct_answer: string;
  explanation: string;
  difficulty: string;
  source_evidence: string;
  topic: string;
  generation_model: string;
  prompt_strategy: string;
  created_at?: string;
}

export interface GenerationRequest {
  passage?: string;
  topic?: string;
  num_questions: number;
  difficulty: string;
  prompt_strategy: string;
  model_name?: string;
  temperature?: number;
}

export interface GenerationResponse {
  success: boolean;
  questions: MCQOutput[];
  total_generated: number;
  latency_ms: number;
  model_used: string;
  prompt_strategy: string;
  error?: string;
}

export interface HealthStatus {
  status: string;
  api_configured: boolean;
  primary_model: string;
  lite_model: string;
  database: string;
  sciq_benchmark_ready: boolean;
}

export interface ExperimentSummary {
  experiment_id: string;
  name: string;
  model?: string;
  strategy?: string;
  status: string;
  total_samples: number;
  valid_schema_rate?: number;
  answer_correctness_rate?: number;
  average_grounding_score?: number;
  average_semantic_similarity?: number;
  average_latency_ms?: number;
  error?: string;
}
