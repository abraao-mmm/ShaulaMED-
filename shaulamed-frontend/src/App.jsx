import React, { useState, useEffect } from 'react';
import StartScreen from './components/StartScreen';
import ConsultationScreen from './components/ConsultationScreen';

function App() {
  const [currentView, setCurrentView] = useState('start');
  const [userId, setUserId] = useState('TEST_UID_THALLES');
  // 1. Criamos um novo estado para guardar o insight da última consulta.
  const [lastInsight, setLastInsight] = useState(null);

  const handleStartConsultation = () => {
    console.log("Iniciando a consulta...");
    // Limpa o insight anterior ao iniciar uma nova consulta
    setLastInsight(null); 
    setCurrentView('consultation');
  };

  // 2. A função agora aceita um parâmetro 'insight'.
  const handleFinishConsultation = (insight) => {
    console.log("Finalizando a consulta e recebendo insight:", insight);
    // Guarda o insight recebido no estado.
    setLastInsight(insight); 
    setCurrentView('start');
  };

  useEffect(() => {
      setCurrentView('start');
  }, []);

  if (currentView === 'start') {
    // 3. Passamos o insight como uma prop para a StartScreen.
    return <StartScreen onStart={handleStartConsultation} insight={lastInsight} />;
  }
  
  if (currentView === 'consultation') {
    return <ConsultationScreen userId={userId} onFinish={handleFinishConsultation} />;
  }

  return null;
}

export default App;