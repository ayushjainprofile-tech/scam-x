import React from 'react';
import { Shield } from 'lucide-react';

interface HeaderProps {
  apiStatus: boolean | null;
}

export const Header: React.FC<HeaderProps> = ({ apiStatus }) => {
  return (
    <header className="header-command-center">
      <div className="header-container">
        <div className="brand-logo">
          <Shield size={20} strokeWidth={1.5} className="brand-icon-inline" />
          <h1 className="brand-name">
            TRUST<span className="brand-highlight">X</span>
          </h1>
          <span className="brand-sub-tag font-mono">v1.2 ENGINE</span>
        </div>

        <div className="header-actions">
          <div className="engine-status-meta">
            <span className={`status-indicator-dot ${apiStatus === true ? 'active' : 'fallback'}`}></span>
            <span className="status-meta-text">
              {apiStatus === true ? 'ENGINE READY' : apiStatus === false ? 'DEGRADED FALLBACK' : 'CONNECTING'}
            </span>
          </div>
          <span className="meta-separator">•</span>
          <span className="hackathon-meta">PS-1 Financial Safety</span>
        </div>
      </div>
    </header>
  );
};



