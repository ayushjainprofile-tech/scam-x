import React from 'react';
import { AlertCircle, CheckCircle2, Search, ShieldCheck } from 'lucide-react';
import type { Signal, VerificationCheck } from '../types';

interface EvidenceCardsProps {
  signals: Signal[];
  verifications: VerificationCheck[];
}

export const EvidenceCards: React.FC<EvidenceCardsProps> = ({ signals, verifications }) => {
  return (
    <div className="evidence-section">
      <div className="section-title-row">
        <Search size={22} className="section-icon" />
        <h3 className="section-heading">Scam Indicators & Verified Evidence ({signals.length})</h3>
      </div>

      {signals.length === 0 ? (
        <div className="empty-signals-card">
          <ShieldCheck size={32} className="safe-check-icon" />
          <p>No high-risk scam indicators were identified in this submission.</p>
        </div>
      ) : (
        <div className="signals-grid">
          {signals.map((signal) => (
            <div key={signal.id} className={`signal-card severity-${signal.severity.toLowerCase()}`}>
              <div className="signal-card-header">
                <span className={`severity-tag severity-tag-${signal.severity.toLowerCase()}`}>
                  {signal.severity} SEVERITY
                </span>
                <span className="category-tag">{signal.category.replace(/_/g, ' ')}</span>
              </div>
              <p className="signal-description">{signal.description}</p>
              {signal.evidence_text && (
                <div className="signal-quote-box">
                  <span className="quote-label">Detected Pattern:</span>
                  <p className="quote-text">"{signal.evidence_text}"</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {verifications && verifications.length > 0 && (
        <div className="verifications-container">
          <h4 className="verifications-title">Reference Layer Verification Checks</h4>
          <div className="verifications-list">
            {verifications.map((check, idx) => (
              <div key={idx} className="verification-item">
                <div className="verif-status-icon">
                  {check.match_found ? (
                    <AlertCircle size={18} className="text-warning" />
                  ) : (
                    <CheckCircle2 size={18} className="text-success" />
                  )}
                </div>
                <div className="verif-details">
                  <div className="verif-source-title">{check.source}</div>
                  <div className="verif-description">{check.details}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
