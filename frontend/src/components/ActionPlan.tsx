import React from 'react';
import { Shield, CheckCircle, XCircle, PhoneCall, ExternalLink } from 'lucide-react';
import type { ActionPlan as ActionPlanType } from '../types';

interface ActionPlanProps {
  actionPlan: ActionPlanType;
}

export const ActionPlanCard: React.FC<ActionPlanProps> = ({ actionPlan }) => {
  const primary_recommendation = actionPlan?.primary_recommendation || 'DO NOT share OTPs, download APKs, or transfer money. Verify directly with official authorities.';
  const do_list = actionPlan?.do_list || ['Verify sender credentials via official banking portal.', 'Report suspicious mobile numbers to 1930 Cyber Crime Helpline.'];
  const dont_list = actionPlan?.dont_list || ['Never install remote screen sharing software or unknown APK apps.', 'Never send money to unverified UPI handles.'];
  const reporting_url = actionPlan?.reporting_url || 'https://cybercrime.gov.in';

  return (
    <div className="action-plan-card">
      <div className="section-title-row">
        <Shield size={22} className="section-icon text-primary" />
        <h3 className="section-heading">Recommended Action Plan</h3>
      </div>

      <div className="primary-recommendation-box">
        <span className="recommendation-badge">Safest Immediate Action</span>
        <p className="recommendation-text">{primary_recommendation}</p>
      </div>

      <div className="actions-dos-donts-grid">
        <div className="dos-column">
          <h4 className="dos-title">
            <CheckCircle size={18} className="text-success" />
            <span>WHAT YOU SHOULD DO</span>
          </h4>
          <ul className="dos-list">
            {do_list.map((item, idx) => (
              <li key={idx} className="do-item">
                <span className="bullet-do">✓</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="donts-column">
          <h4 className="donts-title">
            <XCircle size={18} className="text-danger" />
            <span>WHAT YOU MUST NOT DO</span>
          </h4>
          <ul className="donts-list">
            {dont_list.map((item, idx) => (
              <li key={idx} className="dont-item">
                <span className="bullet-dont">✕</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="helplines-bar">
        <div className="helpline-info">
          <PhoneCall size={20} className="phone-icon" />
          <div>
            <strong>Report Cyber Fraud Immediately</strong>
            <p className="helpline-sub">Government of India Cyber Crime Helpline: 1930</p>
          </div>
        </div>
        <div className="helpline-actions">
          <a href="tel:1930" className="btn-helpline-call">
            Call 1930
          </a>
          <a
            href={reporting_url || "https://cybercrime.gov.in"}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-helpline-portal"
          >
            Report Portal <ExternalLink size={14} />
          </a>
        </div>
      </div>
    </div>
  );
};
