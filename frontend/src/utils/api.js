

const API_BASE_URL = 'http://localhost:8000/api';

export const uploadFiles = async (files) => {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Upload failed');
  }

  return response.json();
};

export const runAnalysis = async (sessionId, filesList, mode = 'both') => {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      files: filesList,
      mode: mode,
    }),
  });

  if (!response.ok) {
    throw new Error('Analysis failed');
  }

  return response.json();
};
