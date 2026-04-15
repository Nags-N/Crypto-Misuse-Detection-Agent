import { useState } from 'react';
import LandingPage from './pages/LandingPage';
import AnalysisPage from './pages/AnalysisPage';
import './App.css'; // Optional for specific app-wide tweaks, but mostly we use index.css

function App() {
  const [currentPage, setCurrentPage] = useState('landing'); // 'landing' or 'analysis'

  return (
    <div className="app-container">
      {currentPage === 'landing' ? (
        <LandingPage onUpload={() => setCurrentPage('analysis')} />
      ) : (
        <AnalysisPage onBack={() => setCurrentPage('landing')} />
      )}
    </div>
  );
}

export default App;
