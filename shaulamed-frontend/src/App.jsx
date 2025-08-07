import React, { useState, useEffect } from 'react';
import StartScreen from './components/StartScreen';
import ConsultationScreen from './components/ConsultationScreen';

function App() {
  const [currentView, setCurrentView] = useState('start');
  const [userId, setUserId] = useState('TEST_UID_THALLES'); 

  const handleStartConsultation = () => {
    console.log("Iniciando a consulta...");
    setCurrentView('consultation');
  };

  const handleFinishConsultation = () => {
    console.log("Finalizando a consulta...");
    setCurrentView('start');
  };

  useEffect(() => {
      setCurrentView('start');
  }, []);

  if (currentView === 'start') {
    return <StartScreen onStart={handleStartConsultation} />;
  }
  
  if (currentView === 'consultation') {
    return <ConsultationScreen userId={userId} onFinish={handleFinishConsultation} />;
  }

  return null; // Renderiza nada se nenhuma view corresponder
}

export default App;