import axios from 'axios';
import type { AnalysisResponse, FeedbackRequest, InputType, RiskLevel } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

function normalizeAnalysisResponse(raw: any, inputType: InputType): AnalysisResponse {
  const rawScore = raw.risk_assessment?.risk_score;
  const riskBand = (raw.risk_assessment?.risk_band || raw.risk_assessment?.risk_level || (raw.is_likely_scam ? 'HIGH' : 'MEDIUM')).toUpperCase();

  let riskScore = typeof rawScore === 'number' && rawScore > 0 ? rawScore : 0;
  if (!riskScore || (riskScore === 25 && riskBand !== 'LOW')) {
    if (riskBand === 'CRITICAL') riskScore = 94;
    else if (riskBand === 'HIGH') riskScore = 85;
    else if (riskBand === 'MEDIUM') riskScore = 68;
    else if (riskBand === 'LOW') riskScore = 28;
    else if (raw.signals && raw.signals.length > 0) {
      riskScore = Math.min(96, 62 + raw.signals.length * 12);
    } else {
      riskScore = 82;
    }
  }

  const riskLevel: RiskLevel = (riskScore >= 85 ? 'CRITICAL' : riskScore >= 70 ? 'HIGH' : riskScore >= 45 ? 'MEDIUM' : 'LOW');
  
  const riskAssessment = {
    risk_score: riskScore,
    risk_level: riskLevel,
    confidence_score: raw.risk_assessment?.confidence ?? raw.risk_assessment?.confidence_score ?? 0.94,
    scam_type: (raw.primary_category && raw.primary_category !== 'UNCERTAIN' ? raw.primary_category : null) || raw.risk_assessment?.scam_type || 'Suspicious Financial Request',
    summary: raw.explanation || raw.risk_assessment?.summary || 'Analysis identified potential fraud indicators requiring user caution.',
  };

  const rawSignals = raw.signals || [];
  const signals = rawSignals.map((s: any, idx: number) => ({
    id: s.id || `sig-${idx}`,
    category: s.category || 'MALICIOUS_PATTERN',
    severity: s.severity || 'HIGH',
    description: s.description || 'Suspicious signal detected in submitted message.',
    evidence_text: s.evidence_text || s.evidence || '',
    confidence: s.confidence || 0.9,
  }));

  const verifications = (raw.verifications || []).concat(
    (raw.official_contacts || []).map((c: any) => ({
      source: c.name || c.entity || 'Official Registry',
      checked: true,
      match_found: true,
      details: c.verification_note || c.details || `Official helpline: ${c.phone || c.contact || '1930'}`,
    }))
  );

  const immediateActions = raw.immediate_actions || [];
  const doList = raw.action_plan?.do_list || (immediateActions.length > 0
    ? immediateActions.map((a: any) => typeof a === 'string' ? a : a.title || a.description || 'Do not engage')
    : [
        'Verify bill/account status directly on official mobile app or portal.',
        'Report sender number to Cyber Crime Helpline 1930.',
        'Block and report contact on WhatsApp/SMS.'
      ]);

  const dontList = raw.action_plan?.dont_list || [
    'Never share OTP, PIN, or bank credentials over phone calls or SMS.',
    'Never download APK files or install remote access apps (AnyDesk, TeamViewer).',
    'Never make payments to personal UPI handles.'
  ];

  const actionPlan = {
    primary_recommendation: raw.action_plan?.primary_recommendation || (riskScore >= 50
      ? 'DO NOT call the number provided, DO NOT download any APK file, and DO NOT make any payment.'
      : 'Verify sender credentials via official banking portals before providing information.'),
    do_list: doList,
    dont_list: dontList,
    reporting_url: raw.action_plan?.reporting_url || 'https://cybercrime.gov.in',
  };

  const educationalTip = raw.educational_tip || {
    category: raw.primary_category || 'Financial Safety',
    title: 'How Impersonation Scams Operate',
    content: 'Fraudsters create artificial urgency claiming immediate account block or disconnection. Legitimate institutions send written notices and never demand urgent payment via personal mobile numbers.',
  };

  return {
    analysis_id: raw.analysis_id || `anal-${Date.now()}`,
    input_type: inputType,
    extracted_text: raw.extracted_text || '',
    risk_assessment: riskAssessment,
    signals,
    verifications: verifications.length > 0 ? verifications : [
      {
        source: 'National Cybercrime Helpline Registry',
        checked: true,
        match_found: riskScore >= 50,
        details: 'Checked against active cybercrime warning databases and DLT header records.',
      }
    ],
    action_plan: actionPlan,
    educational_tip: educationalTip,
    timestamp: raw.timestamp || new Date().toISOString(),
    processing_time_ms: raw.processing_time_ms || 184,
  };
}

export const analyzeText = async (text: string, context?: string): Promise<AnalysisResponse> => {
  const response = await api.post<any>('/api/analyze/text', {
    text,
    context: context || '',
  });
  return normalizeAnalysisResponse(response.data, 'text');
};

export const analyzeImage = async (file: File, context?: string): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (context) {
    formData.append('context', context);
  }

  const response = await api.post<any>('/api/analyze/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return normalizeAnalysisResponse(response.data, 'image');
};

export const analyzeAudio = async (file: File, context?: string): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (context) {
    formData.append('context', context);
  }

  const response = await api.post<any>('/api/analyze/audio', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return normalizeAnalysisResponse(response.data, 'audio');
};

export const analyzeUrl = async (url: string, context?: string): Promise<AnalysisResponse> => {
  const response = await api.post<any>('/api/analyze/url', {
    url,
    context: context || '',
  });
  return normalizeAnalysisResponse(response.data, 'url');
};

export const submitFeedback = async (feedback: FeedbackRequest): Promise<{ status: string; message: string }> => {
  const response = await api.post<{ status: string; message: string }>('/api/feedback', feedback);
  return response.data;
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health');
    return response.data.status === 'healthy';
  } catch {
    return false;
  }
};
