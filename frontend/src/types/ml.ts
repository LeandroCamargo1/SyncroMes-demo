// ── ML Prediction Types ──────────────────────────────────────

export interface OeeDailyForecast {
  date: string;
  oee: number;
  availability: number;
  performance: number;
  quality_rate: number;
  confidence: number;
}

export interface OeePrediction {
  machine_code: string;
  generated_at: string;
  model_used: string;
  forecasts: OeeDailyForecast[];
  trend: 'up' | 'stable' | 'down';
  avg_predicted_oee: number;
}

export interface DowntimeRisk {
  category: string;
  probability: number;
  avg_duration_minutes: number;
  top_reason: string;
}

export interface DowntimePrediction {
  machine_code: string;
  generated_at: string;
  model_used: string;
  overall_risk: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risks_by_category: DowntimeRisk[];
  recommended_actions: string[];
}

export interface DefectForecast {
  defect_type: string;
  probability: number;
  expected_rate_pct: number;
}

export interface QualityPrediction {
  machine_code: string;
  product_code: string | null;
  generated_at: string;
  model_used: string;
  predicted_scrap_rate: number;
  risk_level: string;
  defect_forecasts: DefectForecast[];
  spc_alerts: string[];
}

export interface MoldHealthReport {
  mold_code: string;
  mold_name: string;
  current_cycles: number;
  max_cycles: number | null;
  cycle_usage_pct: number | null;
  days_since_last_maintenance: number | null;
  predicted_days_to_maintenance: number | null;
  health_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  recommendation: string;
}

export interface MoldMaintenancePrediction {
  generated_at: string;
  model_used: string;
  molds: MoldHealthReport[];
}

export interface ModelStatus {
  model_type: string;
  is_trained: boolean;
  last_trained: string | null;
  samples_count: number;
  accuracy_metric: number | null;
}

export interface MlHealth {
  status: string;
  version: string;
  models: ModelStatus[];
}
