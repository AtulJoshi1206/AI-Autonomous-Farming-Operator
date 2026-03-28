import React from 'react';
import ExplanationPanel from './ExplanationPanel';

const TimelineView = ({ timeline, weather, summary, explanation, forecast, selectedLanguage, loading, loadingStage, loadingMessages, ttsLoading }) => {
  if (loading) {
    return (
      <div className="main-view" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '80vh', padding: '40px' }}>
        <h2 style={{ color: '#58a6ff', marginBottom: '30px' }}>Evaluating Agronomic Parameters...</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {loadingMessages?.map((msg, index) => (
            <div key={index} style={{
              display: 'flex', alignItems: 'center', gap: '15px',
              opacity: index <= loadingStage ? 1 : 0.2,
              filter: index <= loadingStage ? 'none' : 'blur(2px)',
              transform: index <= loadingStage ? 'translateX(0)' : 'translateX(-10px)',
              transition: 'all 0.5s ease',
            }}>
              <div style={{
                width: '32px', height: '32px', borderRadius: '50%',
                background: index < loadingStage ? '#238636' : index === loadingStage ? '#1f6feb' : '#30363d',
                boxShadow: index === loadingStage ? '0 0 10px #1f6feb' : 'none',
                display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '1rem',
                color: 'white'
              }}>
                {index < loadingStage ? '✓' : index === loadingStage ? '...' : ''}
              </div>
              <span style={{ 
                fontSize: '1.2rem', 
                color: index < loadingStage ? '#8b949e' : index === loadingStage ? '#c9d1d9' : '#8b949e', 
                fontWeight: index === loadingStage ? 'bold': 'normal' 
              }}>
                {msg}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!timeline || timeline.length === 0) {
    return (
      <div className="main-view">
        <div style={{ textAlign: 'center', opacity: 0.3, marginTop: '20vh' }}>
          <h1 style={{ fontSize: '3rem' }}>AI OPERATOR</h1>
          <p>Execution pipeline ready. Select a scenario or enter manual input.</p>
        </div>
      </div>
    );
  }

  const getStage = (name) => timeline.find(s => s.stage === name)?.output || {};

  const decision = getStage('decision');
  const guardrail = getStage('guardrail');
  const commit = getStage('commit');
  const verify = getStage('verify');
  const recover = getStage('recover');

  const bannerClass = guardrail.status === 'blocked' ? 'blocked' : 
                      recover.recovered ? 'recovery' : 'approved';
  
  let bannerTitle = '';

  if (guardrail.status === 'blocked') {
    bannerTitle = '🛑 SYSTEM BLOCKED — Unsafe conditions detected';
  } else if (recover.recovered) {
    bannerTitle = '⚠️ SYSTEM ADAPTING — Recovery triggered after deviation';
  } else {
    bannerTitle = '🟢 SYSTEM STABLE — Operation executed successfully';
  }

  const StageCard = ({ label, title, statusClass, children }) => (
    <div style={{ width: '100%', marginBottom: '10px' }}>
      <div style={{ fontSize: '0.85rem', color: '#8b949e', marginBottom: '8px', fontWeight: 'bold' }}>{label}</div>
      <div className={`v-card ${statusClass || ''}`}>
        <div className="card-title">{title}</div>
        <div className="card-grid">
          {children}
        </div>
      </div>
      <div style={{ textAlign: 'center', marginTop: '10px', marginBottom: '10px' }}>
        <div className="v-arrow">↓</div>
      </div>
    </div>
  );

  return (
    <div className="main-view">
      {/* FINAL OUTCOME BANNER */}
      <div className={`outcome-banner ${bannerClass}`} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{bannerTitle}</div>
        {ttsLoading && (
          <div style={{ fontSize: '0.85rem', color: '#ffd60a', display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255, 214, 10, 0.1)', padding: '4px 12px', borderRadius: '15px' }}>
             <span className="spinner" style={{ display: 'inline-block', width: '12px', height: '12px', border: '2px solid #ffd60a', borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></span>
             Generating Neural Audio...
          </div>
        )}
      </div>

      {/* GEMINI EXPLANATION */}
      <ExplanationPanel
        explanation={explanation}
        guardrailOutput={guardrail}
        weatherData={weather}
        taskName={decision?.task || 'fertilization'}
        cropName={timeline.find(s => s.stage === 'decision')?.output?.crop || ''}
        location={weather?.location || ''}
        selectedLanguage={selectedLanguage}
      />

      {/* 5-DAY FORECAST ANALYSIS */}
      {forecast && forecast.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{ marginBottom: '10px', fontSize: '0.9rem', fontWeight: 'bold', color: '#c9d1d9' }}>
             📅 Environmental Agent: 5-Day Outlook Analysis
          </div>
          <div className="forecast-container" style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '10px' }}>
            {forecast.map((f, i) => (
              <div key={i} className="forecast-card" style={{ 
                flex: 1, 
                minWidth: '75px', 
                background: '#161b22', 
                border: '1px solid #30363d', 
                borderRadius: '8px', 
                padding: '10px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.6rem', color: '#8b949e' }}>{f.day.includes('-') ? f.day.split('-').slice(1).join('/') : f.day}</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 'bold', margin: '4px 0', color: '#58a6ff' }}>{Math.round(f.temp)}°</div>
                <div style={{ fontSize: '0.55rem', textTransform: 'uppercase', fontWeight: 'bold', color: f.status.toLowerCase().includes('rain') ? '#f85149' : '#3fb950' }}>
                    {f.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* WEATHER HUD */}
      <div>
        <div style={{ marginBottom: '10px', fontSize: '0.9rem', fontWeight: 'bold', color: '#c9d1d9' }}>
          Real-time Environmental Context
        </div>
        <div className="weather-hud">
          <div className="weather-stat">
            <span className="stat-label">Location</span>
            <span className="stat-value">📍 {weather?.location || 'Unknown'}</span>
          </div>
          <div className="weather-stat">
            <span className="stat-label">Rain Prob</span>
            <span className="stat-value" style={{ color: (weather?.rain_prob > 60) ? '#f85149' : '#58a6ff' }}>
                🌧️ {weather?.rain_prob ?? 'N/A'}%
            </span>
          </div>
          <div className="weather-stat">
            <span className="stat-label">Humidity</span>
            <span className="stat-value">💧 {weather?.humidity ?? 'N/A'}%</span>
          </div>
          <div className="weather-stat">
            <span className="stat-label">Temperature</span>
            <span className="stat-value">🌡️ {weather?.temperature ?? 'N/A'}°C</span>
          </div>
        </div>
      </div>

      {/* VERTICAL TIMELINE - STORY MODE */}
      <div className="timeline-flow" style={{ paddingBottom: '100px', marginTop: '20px' }}>
        
        {/* Stage 1: Decision */}
        <StageCard label="1. 🧠 Analytic Agent evaluates strategy" title="Execution Decision Engine">
          <div className="v-prop">
            <div className="v-prop-label">Task</div>
            <div className="v-prop-value" style={{ textTransform: 'capitalize' }}>{decision?.task || 'Fertilization'}</div>
          </div>
          <div className="v-prop">
            <div className="v-prop-label">Recommendation</div>
            <div className="v-prop-value">{decision?.risk_aware_action || 'N/A'}</div>
          </div>
          <div className="v-prop">
            <div className="v-prop-label">Confidence</div>
            <div className={`v-prop-value ${decision?.confidence === 'Low' ? 'error-tag' : 'active-tag'}`}>
              {decision?.confidence || 'N/A'}
            </div>
          </div>
        </StageCard>

        {/* Stage 2: Guardrail */}
        <StageCard 
          label="2.  🛑 Safety Agent validation"
          title="Dynamic Guardrail Policy" 
          statusClass={guardrail?.status === 'blocked' ? 'blocked' : ''}
        >
          <div className="v-prop">
            <div className="v-prop-label">Safety Status</div>
            <div className="v-prop-value" style={{ color: guardrail?.status === 'blocked' ? '#f85149' : '#238636' }}>
              {guardrail?.status?.toUpperCase() || 'N/A'}
            </div>
          </div>
          <div className="v-prop">
            <div className="v-prop-label">Enforcement Log</div>
            <div className="v-prop-value">{guardrail?.reason || 'Policy bypassed'}</div>
          </div>
        </StageCard>

        {/* Stage 3: Commit */}
        <StageCard 
          label="3.  ⚙️ Commitment Agent"
          title="System State Commitment" 
          statusClass={commit?.system_state === 'locked' ? 'locked' : ''}
        >
          <div className="v-prop">
            <div className="v-prop-label">Action Log</div>
            <div className="v-prop-value">{commit?.action || 'No operation committed'}</div>
          </div>
          <div className="v-prop">
            <div className="v-prop-label">Status</div>
            <div className="v-prop-value">{commit?.message || 'N/A'}</div>
          </div>
        </StageCard>

        {/* Stage 4: Verify */}
        <StageCard label="4.  📊 Verification Agent" title="Outcome Verification Trace">
          <div className="v-prop" style={{ gridColumn: '1 / -1' }}>
            <div className="v-prop-label">Trace Matrix Update</div>
            <div className="v-prop-value" style={{ color: verify?.verified ? '#3fb950' : '#8b949e', fontWeight: 'bold' }}>
              {verify?.verified ? '✔ Outcome Verified' : '○ Verification skipped'}
            </div>
          </div>
          <div className="v-prop" style={{ gridColumn: '1 / -1', marginTop: '10px' }}>
            <div className="v-prop-label">Verification Result</div>
            <div className="v-prop-value">{verify?.reason || verify?.message || 'N/A'}</div>
          </div>
        </StageCard>

        {/* Stage 5: Recover */}
        <StageCard 
          label="5.  🔁 Recovery Agent"
          title="Automated Recovery Engine" 
          statusClass={recover?.recovered ? 'recovery-active' : ''}
        >
          <div className="v-prop" style={{ gridColumn: '1 / -1' }}>
            <div className="v-prop-label">Resolution Protocol</div>
            <div className="v-prop-value" style={recover?.recovered ? { color: '#ffd60a', fontWeight: 'bold' } : {}}>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>
                {recover?.message || recover?.resolution || 'System stable. No recovery needed.'}
              </pre>
            </div>
          </div>
        </StageCard>

        {guardrail?.status === 'blocked' && (
          <div style={{ textAlign: 'center', margin: '20px 0', color: '#ff7b72', border: '1px dashed #ff7b72', padding: '15px', borderRadius: '8px', background: 'rgba(255, 123, 114, 0.05)' }}>
            Pipeline status: BLOCKED. Downstream agents executed in simulation mode.
          </div>
        )}

      </div>
    </div>
  );
};

export default TimelineView;
