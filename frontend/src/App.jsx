import React, { useState, useEffect, useRef } from 'react';
import InputForm from './components/InputForm';
import TimelineView from './components/TimelineView';
import './index.css';

function App() {
  const [pipelineState, setPipelineState] = useState({
    timeline: [],
    weather: null,
    forecast: [],
    summary: null,
    explanation: null,
    translated_input: null
  });
  const [selectedLanguage, setSelectedLanguage] = useState('English');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loadingStage, setLoadingStage] = useState(0);
  const [ttsLoading, setTtsLoading] = useState(false);

  useEffect(() => {
    let interval;
    if (loading) {
      setLoadingStage(0);
      interval = setInterval(() => {
        setLoadingStage(prev => prev + 1);
      }, 1000);
    } else {
      setLoadingStage(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const loadingMessages = [
    "🚀 Initializing AI Supervisor...",
    "🌍 Environmental Agent fetching live metrics...",
    "🧠 Global Agronomist AI parsing crop genome...",
    "🛑 Guardrail Agent securing execution boundaries...",
    "⚙️ Commitment Logic synchronizing...",
    "🗣️ Translating to native dialect & generating Neural TTS..."
  ];
  const currentLoadingText = loadingMessages[Math.min(loadingStage, loadingMessages.length - 1)];

  
  const audioRef = useRef(null);

  const playAudioBase64 = (base64String) => {
    if (!base64String) return;
    
    // Stop currently playing audio if any
    if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
    }

    try {
        const audioSrc = `data:audio/mp3;base64,${base64String}`;
        const newAudio = new Audio(audioSrc);
        audioRef.current = newAudio;
        newAudio.play().catch(e => console.error("Audio playback failed:", e));
    } catch (err) {
        console.error("Error playing audio", err);
    }
  };

  const fetchAudio = async (text, language) => {
    if (!text) return;
    setTtsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language }),
      });
      if (response.ok) {
        const result = await response.json();
        if (result.audio_base64) {
          playAudioBase64(result.audio_base64);
        }
      }
    } catch (err) {
      console.error("TTS fetch failed", err);
    } finally {
      setTtsLoading(false);
    }
  };

  const updateState = (result) => {
    setPipelineState({
      timeline: result.timeline || [],
      weather: result.weather,
      forecast: result.forecast || [],
      summary: result.summary,
      explanation: result.explanation,
      translated_input: result.transcription || result.translated_input
    });
    
    if (result.explanation?.detected_language) {
      setSelectedLanguage(result.explanation.detected_language);
    }
    
    // Fetch audio asynchronously so the UI isn't blocked
    if (result.explanation?.explanation_local) {
      fetchAudio(result.explanation.explanation_local, result.explanation.detected_language || 'Hindi');
    }
  };

  const handleRun = async (inputData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...inputData, language: selectedLanguage }),
      });
      if (!response.ok) throw new Error('Backend failed.');
      const result = await response.json();
      updateState(result);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  };

  const handleVoice = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/voice', { method: 'POST', body: formData });
      if (!response.ok) throw new Error('Voice analysis failed.');
      const result = await response.json();
      updateState(result);
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  };

  return (
    <div className="app-container">
      <InputForm 
        onRun={handleRun} 
        onVoice={handleVoice} 
        loading={loading} 
        loadingText={currentLoadingText}
        selectedLanguage={selectedLanguage}
        onLanguageChange={setSelectedLanguage}
      />

      {error && (
        <div style={{ position: 'absolute', bottom: '20px', left: '20px', zIndex: 1000 }}>
          <div className="error-tag" style={{ padding: '10px 20px', borderRadius: '4px' }}>
            {error}
          </div>
        </div>
      )}

      <div className="right-panel">
        <TimelineView
          timeline={pipelineState.timeline}
          weather={pipelineState.weather}
          forecast={pipelineState.forecast}
          summary={pipelineState.summary}
          explanation={pipelineState.explanation}
          selectedLanguage={selectedLanguage}
          loading={loading}
          loadingStage={loadingStage}
          loadingMessages={loadingMessages}
          ttsLoading={ttsLoading}
        />
      </div>
    </div>
  );
}

export default App;
