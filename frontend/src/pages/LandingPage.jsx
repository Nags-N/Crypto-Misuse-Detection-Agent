import React, { useState, useRef } from 'react';
import AppHeader from '../components/layout/AppHeader';
import { UploadCloud } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';
import './LandingPage.css';

function LandingPage({ onUpload }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const { dispatch } = useAnalysis();

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const processFiles = async (fileList) => {
    const javaFiles = Array.from(fileList).filter(f => f.name.endsWith('.java'));
    
    if (javaFiles.length === 0) {
      alert("Please upload .java files only for now.");
      return;
    }

    try {
      // 1. Read files locally for the editor display
      const readPromises = javaFiles.map(file => {
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = (e) => resolve({
            name: file.name,
            size: file.size,
            content: e.target.result
          });
          reader.onerror = reject;
          reader.readAsText(file);
        });
      });
      const parsedFiles = await Promise.all(readPromises);

      // 2. Upload files to the backend to get a sessionId
      const { uploadFiles } = await import('../utils/api.js');
      const uploadResponse = await uploadFiles(javaFiles);

      // 3. Dispatch to context and navigate
      dispatch({ 
        type: 'SET_FILES', 
        payload: { files: parsedFiles, sessionId: uploadResponse.session_id } 
      });
      onUpload(); // Move to Analysis Page
    } catch (err) {
      console.error("Error reading/uploading files:", err);
      alert("Error uploading files to server.");
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await processFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      await processFiles(e.target.files);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="landing-page">
      <AppHeader />
      <main className="landing-main">
        <div className="upload-container">
          <input 
            type="file" 
            ref={fileInputRef} 
            style={{ display: 'none' }} 
            multiple 
            accept=".java"
            onChange={handleFileInput}
          />
          <div 
            className={`upload-box ${isDragging ? 'dragging' : ''}`} 
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={triggerFileInput}
          >
            <UploadCloud size={48} className="upload-icon" />
            <h2>Drag & Drop</h2>
            <p>Java files (.java)</p>
            <button className="browse-btn" type="button">Browse Files</button>
            <p className="upload-help">Supports: .java | Max 50 files</p>
          </div>
          
          <div className="actions">
            {/* The run analysis button is somewhat redundant if upload triggers it immediately, 
                but let's keep it visually intact for now, triggering the file input. */}
            <button className="run-analysis-btn" onClick={triggerFileInput}>
              ▶ Choose Files to Analyze
            </button>
          </div>
          
          <div className="divider">
            <span>or</span>
          </div>
          
          <div className="benchmark-loader">
            <label>Load benchmark dataset:</label>
            <select>
              <option>CryptoAPI-Bench (Stub)</option>
              <option>Hard Cases (Stub)</option>
            </select>
          </div>
        </div>
      </main>
    </div>
  );
}

export default LandingPage;
