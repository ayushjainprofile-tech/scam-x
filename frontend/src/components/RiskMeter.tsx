import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, Info, Clock, CheckCircle } from 'lucide-react';
import type { RiskAssessment } from '../types';

interface RiskMeterProps {
  assessment: RiskAssessment;
  processingTimeMs: number;
}

export const RiskMeter: React.FC<RiskMeterProps> = ({ assessment, processingTimeMs }) => {
  const { risk_score, risk_level, confidence_score, scam_type, summary } = assessment;

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'var(--risk-critical)';
      case 'HIGH':
        return 'var(--risk-high)';
      case 'MEDIUM':
        return 'var(--risk-medium)';
      case 'LOW':
        return 'var(--risk-low)';
      default:
        return 'var(--risk-safe)';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'CRITICAL':
      case 'HIGH':
        return <ShieldAlert size={36} className="risk-icon-critical" />;
      case 'MEDIUM':
        return <AlertTriangle size={36} className="risk-icon-medium" />;
      case 'LOW':
        return <Info size={36} className="risk-icon-low" />;
      default:
        return <ShieldCheck size={36} className="risk-icon-safe" />;
    }
  };

  const riskColor = getRiskColor(risk_level);
  const confidencePercent = Math.round(confidence_score * 100);

  return (
    <div className={`risk-meter-card risk-border-${risk_level.toLowerCase()}`}>
      <div className="risk-header">
        <div className="risk-badge-icon">
          {getRiskIcon(risk_level)}
        </div>
        <div className="risk-title-wrapper">
          <div className="risk-level-row">
            <span className={`risk-pill risk-pill-${risk_level.toLowerCase()}`}>
              {risk_level} RISK DETECTED
            </span>
            <span className="confidence-pill">
              <CheckCircle size={12} /> {confidencePercent}% Engine Confidence
            </span>
            <span className="timing-pill">
              <Clock size={12} /> {processingTimeMs}ms
            </span>
          </div>
          <h2 className="scam-type-title">{scam_type}</h2>
        </div>
      </div>

      <div className="gauge-container">
        <div className="gauge-label-row">
          <span>Safe (0)</span>
          <span className="gauge-score-display" style={{ color: riskColor }}>
            Score: {risk_score} / 100
          </span>
          <span>Critical (100)</span>
        </div>
        <div className="gauge-track">
          <div
            className="gauge-fill"
            style={{
              width: `${Math.max(5, Math.min(100, risk_score))}%`,
              backgroundColor: riskColor,
            }}
          />
        </div>
      </div>

      <div className="risk-summary-box">
        <h4 className="summary-title">Assessment Executive Summary</h4>
        <p className="summary-text">{summary}</p>
      </div>
    </div>
  );
};
