import React from 'react';
import { ShieldAlert, ShieldCheck } from 'lucide-react';
import { useAnalysis } from '../../context/AnalysisContext';
import './AIInsightPanel.css';

function VerdictBadge({ verdict }) {
  if (!verdict) return null;
  const isSecure = verdict.toLowerCase() === 'secure' || verdict.toLowerCase() === 'safe';
  return (
    <div className={`verdict-badge ${isSecure ? 'secure' : 'insecure'}`}>
      {isSecure ? <ShieldCheck size={18} /> : <ShieldAlert size={18} />}
      <span>{verdict.toUpperCase()}</span>
    </div>
  );
}

function ConfidenceMeter({ level }) {
  if (!level) return null;
  const colors = { high: 'var(--severity-critical)', medium: 'var(--severity-warning)', low: 'var(--severity-info)' };
  const getWidth = () => {
    switch (level.toLowerCase()) {
      case 'high': return '90%';
      case 'medium': return '60%';
      case 'low': return '30%';
      default: return '0%';
    }
  };
  return (
    <div className="confidence-meter">
      <span className="label">Confidence: {level.toUpperCase()}</span>
      <div className="bar-bg">
        <div className="bar-fill" style={{ width: getWidth(), backgroundColor: colors[level.toLowerCase()] || colors.low }}></div>
      </div>
    </div>
  );
}

function ReasoningSteps({ trace }) {
  if (!trace) return null;
  
  // Parse trace by generic markdown headers or the custom `---` markers
  const sections = [];
  const parts = trace.split(/---(.*?)---/g);
  
  if (parts.length > 1) {
    for (let i = 1; i < parts.length; i += 2) {
      sections.push({
        title: parts[i].trim(),
        content: (parts[i+1] || "").trim()
      });
    }
  } else {
    sections.push({
      title: "Reasoning Trace",
      content: trace.trim()
    });
  }

  return (
    <div className="reasoning-steps card">
      <h3>Reasoning Steps</h3>
      {sections.map((sec, idx) => (
        <details key={idx} className="step" open={idx === sections.length - 1}>
          <summary>{idx + 1}. {sec.title}</summary>
          <p style={{ whiteSpace: 'pre-wrap' }}>{sec.content}</p>
        </details>
      ))}
    </div>
  );
}

function AIInsightPanel() {
  const { state } = useAnalysis();
  
  const selectedFile = state.selectedFile;
  const fileResult = selectedFile ? state.results[selectedFile] : null;

  if (!fileResult) {
    if (state.analysisStatus === 'analyzing') {
      return (
        <div className="ai-insight-panel">
          <div className="card" style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
             <p>Analyzing code... please wait.</p>
          </div>
        </div>
      );
    }
    return (
      <div className="ai-insight-panel">
        <div className="card" style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
          Select an analyzed file to see AI insights.
        </div>
      </div>
    );
  }

  // Map from agent report and rule based report
  const agent = fileResult.agent || {};
  const rb = fileResult.rule_based || {};
  
  let verdict = agent.label || fileResult.verdict || 'unknown';
  if (verdict === 'unknown' && rb.label) {
     verdict = rb.label;
  }
  const confidence = agent.confidence || 'medium';
  
  // Explanation logic
  const findings = agent.findings || [];
  let explanation = findings.length > 0 ? findings[0].explanation : agent.reasoning_trace?.substring(0, 150) + "...";
  
  if (!explanation && rb.triggered_rules && rb.triggered_rules.length > 0) {
      explanation = `Rule based engine triggered rules: ${rb.triggered_rules.join(", ")}`;
  } else if (!explanation) {
      explanation = "No specific explanation was provided for this file.";
  }

  // Recommendations Generation
  let recommendation = agent.recommendation; // If the agent provided one
  let recCodeSnippet = null;

  // Fallback Rule-based Recommendations
  if (!recommendation && rb.triggered_rules) {
      if (rb.triggered_rules.includes("ecb_mode") || rb.triggered_rules.includes("ECB")) {
          recommendation = "Use AES with an authenticated mode like GCM instead of ECB.";
          recCodeSnippet = `Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");`;
      } else if (rb.triggered_rules.includes("hardcoded_key_string") || rb.triggered_rules.includes("hardcoded")) {
          recommendation = "Never hardcode cryptographic keys. Load them from a secure vault or environment variables.";
      } else {
          recommendation = "Consider reviewing cryptographic operations against OWASP best practices.";
      }
  }

  return (
    <div className="ai-insight-panel">
      
      <div className="status-row">
        <VerdictBadge verdict={verdict} />
        {verdict !== 'unknown' && <ConfidenceMeter level={confidence} />}
      </div>

      <div className="card explanation-card">
        <h3>Explanation</h3>
        <p>{explanation}</p>
      </div>

      <ReasoningSteps trace={agent.reasoning_trace} />

      <div className="card recommendation-card">
        <h3>{recommendation ? "Recommendation" : "Details"}</h3>
        <p>{recommendation || "Review the analysis trace for more details."}</p>
        
        {recCodeSnippet && (
           <pre><code>{recCodeSnippet}</code></pre>
        )}
      </div>
      
    </div>
  );
}

export default AIInsightPanel;
