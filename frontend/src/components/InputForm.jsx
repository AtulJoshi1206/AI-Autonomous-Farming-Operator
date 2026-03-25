import React, { useState, useRef } from 'react';

const InputForm = ({ onRun, onVoice, loading, loadingText, selectedLanguage, onLanguageChange }) => {
  const [formData, setFormData] = useState({
    task: '',
    crop: '',
    location: 'Moradabad',
    soil: 'medium'
  });
  
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const languages = ['English', 'Hindi', 'Marathi', 'Gujarati', 'Punjabi'];

  const handleScenario = (key) => {
    if (key === 'normal') {
        const data = { task: 'fertilization', crop: 'wheat', location: 'Moradabad', soil: 'medium', rain_prob: 20 };
        setFormData({ ...data });
        onRun({ ...data });
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onRun({ ...formData, rain_prob: null });
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (event) => audioChunksRef.current.push(event.data);
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const voiceFormData = new FormData();
        voiceFormData.append('file', audioBlob, 'recording.wav');
        voiceFormData.append('location', formData.location || '');
        voiceFormData.append('crop', formData.crop || '');
        voiceFormData.append('soil', formData.soil || '');
        onVoice(voiceFormData);
      };
      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      alert("Microphone access is required.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) { mediaRecorderRef.current.stop(); setIsRecording(false); }
  };

  return (
    <div className="left-panel">
      <h1>🚜 Autonomous Farming Operator</h1>
      
      <div className="language-toggle" style={{ marginBottom: '20px', display: 'flex', gap: '5px' }}>
        {languages.map(lang => (
            <button key={lang} className={`lang-btn ${selectedLanguage === lang ? 'active' : ''}`} onClick={() => onLanguageChange(lang)}
                style={{ padding: '5px 12px', borderRadius: '20px', border: '1px solid #30363d', background: selectedLanguage === lang ? '#1f6feb' : '#21262d', color: '#c9d1d9', cursor: 'pointer', fontSize: '0.75rem', transition: 'all 0.3s' }}>
                {lang === 'English' ? 'EN' : lang === 'Hindi' ? 'हिन्दी' : lang === 'Marathi' ? 'मराठी' : lang === 'Gujarati' ? 'ગુજરાતી' : 'ਪੰਜਾਬੀ'}
            </button>
        ))}
      </div>

      <div className="scenario-buttons" style={{ marginBottom: '30px' }}>
        <button className="scenario-btn" onClick={() => handleScenario('normal')}>Reset to Normal</button>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '25px' }}>
            <div style={{ flex: 1, textAlign: 'center' }}>
                <div style={{ fontSize: '0.8rem', color: '#8b949e', marginBottom: '10px' }}>
                    {isRecording ? 'Listening...' : 'Voice Interface (Speak Now)'}
                </div>
                <button type="button" className={`voice-orb ${isRecording ? 'active' : ''}`} onMouseDown={startRecording} onMouseUp={stopRecording} onMouseLeave={stopRecording}
                    style={{ width: '60px', height: '60px', borderRadius: '50%', border: '2px solid #1f6feb', background: isRecording ? '#1f6feb' : 'rgba(31, 111, 235, 0.1)', color: 'white', fontSize: '1.5rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto', boxShadow: isRecording ? '0 0 20px #1f6feb' : 'none', transition: 'all 0.3s' }}>
                    {isRecording ? '🎙️' : '🎤'}
                </button>
            </div>
        </div>

        <div className="form-group">
          <label>Deployment Location</label>
          <input type="text" name="location" value={formData.location} onChange={handleChange} placeholder="Search City..." required />
        </div>

        <div className="form-group">
          <label>Operational Task</label>
          <input type="text" name="task" value={formData.task} onChange={handleChange} placeholder="e.g. Planting, Harvesting, Watering..." required />
        </div>

        <div className="form-group">
          <label>Target Crop Profile</label>
          <input type="text" name="crop" value={formData.crop} onChange={handleChange} placeholder="e.g. Roses, Kannu, Wheat, Dragon Fruit..." required />
        </div>

        <div className="form-group">
          <label>On-Site Soil Sensor</label>
          <select name="soil" value={formData.soil || ''} onChange={handleChange}>
            <option value="dry">Dry</option>
            <option value="medium">Medium</option>
            <option value="wet">Wet</option>
            <option value="">Off (Simulate Sensor Fail)</option>
          </select>
        </div>

        <button type="submit" className="submit-btn" disabled={loading} style={{ marginTop: '20px' }}>
          {loading ? loadingText : '🚀 Execute Decision'}
        </button>
      </form>
    </div>
  );
};

export default InputForm;
