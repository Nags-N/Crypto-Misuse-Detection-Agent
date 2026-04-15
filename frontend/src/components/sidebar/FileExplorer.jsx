import React from 'react';
import { FileCode, ShieldAlert, ShieldCheck } from 'lucide-react';
import { useAnalysis } from '../../context/AnalysisContext';
import './Sidebar.css';

function FileExplorer() {
  const { state, dispatch } = useAnalysis();

  if (!state.files || state.files.length === 0) {
    return <div className="sidebar-section">No files uploaded.</div>;
  }

  return (
    <div className="sidebar-section file-explorer">
      <h3 className="section-title">Files</h3>
      <ul className="file-list">
        {state.files.map(f => {
          const result = state.results[f.name];
          const isSecure = result ? result.agent?.label === 'secure' || result.rule_based?.label === 'secure' || result.verdict === 'secure' || result.verdict === 'safe' : null;
          const isInsecure = result ? result.agent?.label === 'insecure' || result.rule_based?.label === 'insecure' || result.verdict === 'insecure' : null;
          
          return (
            <li 
              key={f.name} 
              className={`file-item ${state.selectedFile === f.name ? 'active' : ''}`}
              onClick={() => dispatch({ type: 'SET_SELECTED_FILE', payload: f.name })}
            >
              <FileCode size={16} className="file-icon" />
              <span className="file-name">{f.name}</span>
              {isInsecure && <ShieldAlert size={14} className="status-icon insecure" />}
              {isSecure && <ShieldCheck size={14} className="status-icon secure" />}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default FileExplorer;
