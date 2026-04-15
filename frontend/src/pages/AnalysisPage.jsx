import React from 'react';
import AppHeader from '../components/layout/AppHeader';
import PanelLayout from '../components/layout/PanelLayout';
import FileExplorer from '../components/sidebar/FileExplorer';
import ScanOverview from '../components/sidebar/ScanOverview';
import CodeViewer from '../components/editor/CodeViewer';
import AIInsightPanel from '../components/insights/AIInsightPanel';
import { useAnalysis } from '../context/AnalysisContext';
import { runAnalysis } from '../utils/api';
import './AnalysisPage.css';

function AnalysisPage({ onBack }) {
  const { state, dispatch } = useAnalysis();

  React.useEffect(() => {
    // Only analyze if we have a session and haven't analyzed yet
    if (state.sessionId && state.analysisStatus === 'idle') {
      const analyze = async () => {
        dispatch({ type: 'SET_STATUS', payload: 'analyzing' });
        try {
          const fileNames = state.files.map(f => f.name);
          const result = await runAnalysis(state.sessionId, fileNames);
          dispatch({ type: 'SET_RESULTS', payload: result });
        } catch (err) {
          console.error("Analysis failed:", err);
          dispatch({ type: 'SET_STATUS', payload: 'error' });
          alert("Analysis failed. Please check the server logs.");
        }
      };
      
      analyze();
    }
  }, [state.sessionId, state.analysisStatus, state.files, dispatch]);

  const handleBack = () => {
    dispatch({ type: 'CLEAR_ALL' });
    onBack();
  };

  const isAnalyzing = state.analysisStatus === 'analyzing';

  // Construct status bar text
  let statusText = "Ready to analyze";
  if (isAnalyzing) statusText = "Analyzing... (This might take a while)";
  else if (state.analysisStatus === 'done') {
    statusText = `Analysis complete • ${state.scanSummary.insecureCount} issue(s) found`;
  }

  return (
    <div className="analysis-page">
      <AppHeader 
        onBack={handleBack} 
        title={isAnalyzing ? "Analyzing Files..." : "Analysis Results"} 
        status={statusText} 
      />
      <PanelLayout
        left={<><FileExplorer /><ScanOverview /></>}
        center={<CodeViewer />}
        right={<AIInsightPanel />}
      />
    </div>
  );
}

export default AnalysisPage;
