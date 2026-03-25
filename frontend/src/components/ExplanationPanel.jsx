import React, { useState } from 'react';

const ExplanationPanel = ({ explanation, guardrailOutput, weatherData, cropName, taskName, location, selectedLanguage }) => {
  const [whatIfResult, setWhatIfResult] = useState(null);
  const [loadingWhatIf, setLoadingWhatIf] = useState(false);
  const [showPanel, setShowPanel] = useState(true);

  if (!explanation) return null;

  const handleWhatIf = async () => {
    setLoadingWhatIf(true);
    try {
      const resp = await fetch('http://localhost:8000/what-if', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          crop: cropName || 'wheat',
          task: taskName || 'fertilization',
          location: location,
          rain_prob: weatherData?.rain_prob || 0,
          reason: guardrailOutput?.reason || 'System block',
          action: 'proceeded with execution anyway',
          language: selectedLanguage
        })
      });
      const data = await resp.json();
      setWhatIfResult(data);
    } catch (e) {
      setWhatIfResult({ risk_en: 'Could not fetch simulation.', risk_local: 'सिमुलेशन उपलब्ध नहीं है।' });
    } finally {
      setLoadingWhatIf(false);
    }
  };

  const labels = {
    English: { reasoning: "System Reasoning", field: "Field Advisory", risk: "Risk Simulation" },
    Hindi: { reasoning: "सिस्टम तर्क", field: "कृषि सुझाव", risk: "जोखिम विश्लेषण" },
    Marathi: { reasoning: "सिस्टमचे तर्क", field: "शेती सल्ला", risk: "जोखिम विश्लेषण" },
    Gujarati: { reasoning: "સિસ્ટમ તર્ક", field: "ખેતી સલાહ", risk: "જોખમ વિશ્લેષણ" }
  };

  const curr = labels[selectedLanguage] || labels['English'];

  return (
    <div className="explanation-panel">
      <div className="exp-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className="exp-title">🧠 AI Explanation (Human-Friendly)</span>
          <span className="exp-badge">Gemini</span>
        </div>
        <button
          className="collapse-btn"
          onClick={() => setShowPanel(v => !v)}
        >{showPanel ? '▲' : '▼'}</button>
      </div>

      {showPanel && (
        <div className="exp-body">
          {/* Main Explanation */}
          <div className="exp-block">
            <div className="exp-label" style={{ marginBottom: '5px', color: '#8b949e' }}>🌍 {labels.English.reasoning} (English)</div>
            <div className="exp-text" style={{ paddingBottom: '12px', borderBottom: '1px solid #30363d', marginBottom: '12px' }}>
              {explanation.explanation_en}
            </div>
            {selectedLanguage !== 'English' && (
              <>
                <div className="exp-label" style={{ marginBottom: '5px', color: '#8b949e' }}>🚩 {curr.reasoning} ({selectedLanguage})</div>
                <div className="exp-text">
                  {explanation.explanation_local}
                </div>
              </>
            )}
          </div>

          {/* What If Button */}
          <div style={{ marginTop: '10px' }}>
            <button
              className="whatif-btn"
              onClick={handleWhatIf}
              disabled={loadingWhatIf}
            >
              {loadingWhatIf ? 'Simulating...' : '⚠️ What if I ignore this?'}
            </button>
          </div>

          {/* What If Result */}
          {whatIfResult && (
            <div className="whatif-result" style={{ marginTop: '15px' }}>
              <div className="exp-label" style={{ marginBottom: '10px' }}>🚨 {labels.English.risk} / {curr.risk}</div>
              
              <div style={{ paddingBottom: '12px', borderBottom: '1px solid #30363d', marginBottom: '12px' }}>
                <div className="whatif-row">
                  <span className="wi-label">Risk (EN)</span>
                  <span className="wi-value">{whatIfResult.risk_en}</span>
                </div>
                {selectedLanguage !== 'English' && (
                  <div className="whatif-row">
                    <span className="wi-label">Risk ({selectedLanguage.substring(0,2)})</span>
                    <span className="wi-value">{whatIfResult.risk_local}</span>
                  </div>
                )}
              </div>

              <div>
                <div className="whatif-row">
                  <span className="wi-label">Impact (EN)</span>
                  <span className="wi-value">{whatIfResult.impact_en}</span>
                </div>
                {selectedLanguage !== 'English' && (
                  <div className="whatif-row">
                    <span className="wi-label">Impact ({selectedLanguage.substring(0,2)})</span>
                    <span className="wi-value">{whatIfResult.impact_local}</span>
                  </div>
                )}
              </div>

            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ExplanationPanel;
