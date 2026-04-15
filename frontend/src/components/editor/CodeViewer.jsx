import React, { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { useAnalysis } from '../../context/AnalysisContext';

function CodeViewer() {
  const { state } = useAnalysis();
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const decorationsRef = useRef([]);
  
  const selectedFile = state.files.find(f => f.name === state.selectedFile);
  const code = selectedFile ? selectedFile.content : '// No file selected';
  const fileResult = selectedFile ? state.results[selectedFile.name] : null;

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    applyDecorations();
  };

  const applyDecorations = () => {
    if (!editorRef.current || !monacoRef.current || !fileResult) return;

    const editor = editorRef.current;
    const monaco = monacoRef.current;
    const newDecorations = [];

    // Collect findings that map to specific lines
    const findings = fileResult.agent?.findings || [];
    
    findings.forEach(finding => {
      if (finding.line_hint && !isNaN(parseInt(finding.line_hint))) {
        const lineNum = parseInt(finding.line_hint);
        newDecorations.push({
          range: new monaco.Range(lineNum, 1, lineNum, 1),
          options: {
            isWholeLine: true,
            className: "highlight-insecure-line",
            glyphMarginClassName: "glyph-insecure",
            glyphMarginHoverMessage: { value: `**Security Issue:** ${finding.explanation}` }
          }
        });
      }
    });

    decorationsRef.current = editor.deltaDecorations(decorationsRef.current, newDecorations);
  };

  // Re-apply decorations when selected file or results change
  useEffect(() => {
    applyDecorations();
  }, [state.selectedFile, state.results]);

  return (
    <div style={{ height: '100%', width: '100%', backgroundColor: 'var(--bg-primary)' }}>
      {selectedFile ? (
        <Editor
          height="100%"
          language="java"
          theme="vs-dark"
          value={code}
          onMount={handleEditorDidMount}
          options={{
            readOnly: true,
            minimap: { enabled: false },
            lineNumbers: "on",
            scrollBeyondLastLine: false,
            fontSize: 14,
            fontFamily: "var(--font-mono)",
            padding: { top: 16 },
            glyphMargin: true // Essential for the red dot margin to work
          }}
        />
      ) : (
        <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>
          Please select a file from the sidebar to view code.
        </div>
      )}
    </div>
  );
}

export default CodeViewer;
