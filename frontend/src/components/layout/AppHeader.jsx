import React from 'react';
import { Lock, ArrowLeft } from 'lucide-react';
import './AppHeader.css';

function AppHeader({ onBack, title, status }) {
  return (
    <header className="app-header">
      <div className="header-left">
        {onBack && (
          <button className="back-btn" onClick={onBack}>
            <ArrowLeft size={18} />
            <span>Back</span>
          </button>
        )}
        <div className="logo-container">
          <Lock size={20} className="logo-icon" />
          <h1 className="logo-text">CryptoGuard AI</h1>
        </div>
      </div>
      
      {title && <div className="header-title">{title}</div>}
      
      <div className="header-right">
        {status && <span className="header-status">{status}</span>}
      </div>
    </header>
  );
}

export default AppHeader;
