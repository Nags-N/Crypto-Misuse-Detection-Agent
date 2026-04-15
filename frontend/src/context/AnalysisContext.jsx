import React, { createContext, useContext, useReducer } from 'react';

const initialState = {
  files: [],              // Array of { name, content, size }
  selectedFile: null,     // string: name of the currently selected file
  analysisStatus: 'idle', // 'idle' | 'uploading' | 'analyzing' | 'done' | 'error'
  results: {},            // Keyed by filename
  scanSummary: {
    totalFiles: 0,
    insecureCount: 0,
    secureCount: 0
  }
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_FILES':
      return { 
        ...state, 
        files: action.payload.files,
        sessionId: action.payload.sessionId,
        selectedFile: action.payload.files.length > 0 ? action.payload.files[0].name : null,
        scanSummary: { ...state.scanSummary, totalFiles: action.payload.files.length }
      };
    case 'SET_SELECTED_FILE':
      return { ...state, selectedFile: action.payload };
    case 'SET_STATUS':
      return { ...state, analysisStatus: action.payload };
    case 'SET_RESULTS':
      return { 
        ...state, 
        results: action.payload.results,
        scanSummary: action.payload.summary,
        analysisStatus: 'done'
      };
    case 'CLEAR_ALL':
      return initialState;
    default:
      return state;
  }
}

const AnalysisContext = createContext();

export function AnalysisProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <AnalysisContext.Provider value={{ state, dispatch }}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  return useContext(AnalysisContext);
}
