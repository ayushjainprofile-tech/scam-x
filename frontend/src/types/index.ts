export type RiskLevel = 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type SignalSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type SignalCategory = 'URGENCY' | 'FINANCIAL_REQUEST' | 'CREDENTIAL_HARVESTING' | 'IMPERSONATION' | 'SUSPICIOUS_LINK' | 'MALICIOUS_PATTERN' | 'BEHAVIORAL_MANIPULATION';
export type InputType = 'text' | 'image' | 'audio' | 'url';

export interface Signal {
  id: string;
  category: SignalCategory;
  severity: SignalSeverity;
  description: string;
  evidence_text: string;
  confidence: number;
}

export interface VerificationCheck {
  source: string;
  checked: boolean;
  match_found: boolean;
  details: string;
}

export interface ActionPlan {
  primary_recommendation: string;
  do_list: string[];
  dont_list: string[];
  helpline_numbers?: Record<string, string>;
  reporting_url?: string;
}

export interface RiskAssessment {
  risk_score: number; // 0 - 100
  risk_level: RiskLevel;
  confidence_score: number; // 0 - 1.0
  scam_type: string;
  summary: string;
}

export interface EducationalTip {
  title: string;
  content: string;
  category: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  input_type: InputType;
  extracted_text?: string;
  risk_assessment: RiskAssessment;
  signals: Signal[];
  verifications: VerificationCheck[];
  action_plan: ActionPlan;
  educational_tip: EducationalTip;
  timestamp: string;
  processing_time_ms: number;
}

export interface FeedbackRequest {
  analysis_id: string;
  is_accurate: boolean;
  user_comment?: string;
  actual_scam_type?: string;
}
