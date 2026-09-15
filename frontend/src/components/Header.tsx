import React from 'react';
import { ShieldAlert, Zap } from 'lucide-react';

interface HeaderProps {
  apiStatus: boolean | null;
}

export const Header: React.FC<HeaderProps> = ({ apiStatus }) => {
  return (
    <header className="header-glass">
      <div className="header-container">
        <div className="brand-logo">
          <div className="logo-icon-wrapper">
            <ShieldAlert className="logo-icon" size={28} />
          </div>
          <div className="brand-titles">
            <h1 className="brand-name">
              SCAM<span className="brand-highlight">X</span> <span className="ai-badge">AI</span>
            </h1>
            <p className="brand-tagline">Multimodal Scam Risk Intelligence & Decision Engine</p>
          </div>
        </div>

        <div className="header-actions">
          <div className={`status-badge ${apiStatus === true ? 'status-online' : apiStatus === false ? 'status-offline' : 'status-checking'}`}>
            <span className="status-dot"></span>
            <span className="status-text">
              {apiStatus === true ? 'Engine Active' : apiStatus === false ? 'Engine Offline' : 'Connecting...'}
            </span>
          </div>
          <div className="hackathon-tag">
            <Zap size={14} />
            <span>PS-1 Financial Safety</span>
          </div>
        </div>
      </div>
    </header>
  );
};
