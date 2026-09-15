import React, { useState, useEffect } from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, Info, Clock, CheckCircle } from 'lucide-react';
import type { RiskAssessment } from '../types';

interface RiskMeterProps {
  assessment: RiskAssessment;
  processingTimeMs: number;
}

export const RiskMeter: React.FC<RiskMeterProps> = ({ assessment, processingTimeMs }) => {
  const { risk_score, risk_level, confidence_score, scam_type, summary } = assessment;

  // Animated count-up for score
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = Math.max(0, Math.min(100, risk_score || 0));
    if (end === 0) {
      setAnimatedScore(0);
      return;
    }

    const duration = 800;
    const stepTime = 16;
    const steps = duration / stepTime;
    const increment = end / steps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setAnimatedScore(end);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.floor(start));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [risk_score]);

  const getRiskColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
      case 'HIGH':
        return 'var(--risk-red)';
      case 'MEDIUM':
        return 'var(--risk-amber)';
      case 'LOW':
      case 'SAFE':
        return 'var(--risk-green)';
      default:
        return 'var(--risk-amber)';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL':
      case 'HIGH':
        return <ShieldAlert size={36} color="var(--risk-red)" />;
      case 'MEDIUM':
        return <AlertTriangle size={36} color="var(--risk-amber)" />;
      case 'LOW':
      case 'SAFE':
        return <ShieldCheck size={36} color="var(--risk-green)" />;
      default:
        return <Info size={36} color="var(--cream)" />;
    }
  };

  const riskColor = getRiskColor(risk_level);
  const confidencePercent = Math.round((confidence_score || 0.92) * 100);

  return (
    <div className="risk-meter-3d-wrapper">
      <div className="risk-card-3d">
        <div className="risk-card-top-bar">
          <div className="risk-header-left">
            <div className="risk-badge-icon">
              {getRiskIcon(risk_level)}
            </div>
            <div className="risk-meta-info">
              <div className="risk-level-row">
                <span className={`risk-pill risk-pill-${(risk_level || 'MEDIUM').toLowerCase()}`}>
                  {risk_level || 'EVALUATED'} RISK DETECTED
                </span>
                <span className="confidence-pill">
                  <CheckCircle size={12} /> {confidencePercent}% Engine Confidence
                </span>
                <span className="timing-pill">
                  <Clock size={12} /> {processingTimeMs}ms
                </span>
              </div>
              <h2 className="scam-type-title">{scam_type || 'Suspicious Content Analysis'}</h2>
            </div>
          </div>
        </div>

        {/* 3D Score Section */}
        <div className="score-hero-3d">
          <div className="score-val-3d font-mono tabular-nums" style={{ color: riskColor }}>
            {animatedScore}
          </div>
          <div className="score-meta-3d">
            <div className="score-max font-mono">/ 100</div>
            <div className="score-label-sub">THREAT INDEX</div>
          </div>
        </div>

        {/* Dynamic Animated Gauge Track */}
        <div className="gauge-container">
          <div className="gauge-label-row">
            <span>Safe (0)</span>
            <span className="gauge-score-display" style={{ color: riskColor }}>
              Threat Level: {animatedScore} / 100
            </span>
            <span>Critical (100)</span>
          </div>
          <div className="gauge-track">
            <div
              className="gauge-fill"
              style={{
                width: `${Math.max(6, Math.min(100, animatedScore))}%`,
                backgroundColor: riskColor,
              }}
            />
          </div>
        </div>

        {/* Executive Summary Box */}
        <div className="risk-summary-box">
          <h4 className="summary-title">ASSESSMENT EXECUTIVE SUMMARY</h4>
          <p className="summary-text">{summary}</p>
        </div>
      </div>
    </div>
  );
};
