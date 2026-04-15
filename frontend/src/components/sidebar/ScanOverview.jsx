import React from 'react';
import { useAnalysis } from '../../context/AnalysisContext';
import './Sidebar.css';

function ScanOverview() {
  const { state } = useAnalysis();
  const summary = state.scanSummary;

  return (
    <div className="sidebar-section scan-overview">
      <h3 className="section-title">Scan Overview</h3>
      <div className="stats-grid">
        <div className="stat-box">
          <span className="stat-val">{summary.totalFiles || 0}</span>
          <span className="stat-label">Files</span>
        </div>
        <div className="stat-box insecure">
          <span className="stat-val">{summary.insecureCount || 0}</span>
          <span className="stat-label">Issues</span>
        </div>
        <div className="stat-box secure">
          <span className="stat-val">{summary.secureCount || 0}</span>
          <span className="stat-label">Secure</span>
        </div>
      </div>
    </div>
  );
}

export default ScanOverview;
