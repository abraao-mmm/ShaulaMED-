import React, { useState, useEffect } from 'react';
import StartScreen from './components/StartScreen';
import ConsultationScreen from './components/ConsultationScreen'; // Importa a nova tela

function App() {
  const [currentView, setCurrentView] = useState('start');
  
  // Estado para guardar o ID do utilizador logado (será implementado no futuro)
  // Por agora, usamos um ID de teste
  const [userId, setUserId] = useState('TEST_UID_THALLES'); 

  const handleStartConsultation = () => {
    console.log("Iniciando a consulta...");
    setCurrentView('consultation');
  };

  const handleFinishConsultation = () => {
    console.log("Finalizando a consulta...");
    setCurrentView('start'); // Volta para a tela inicial
  };

  // Simula o login e define o ecrã inicial
  useEffect(() => {
      // No futuro, aqui virá a lógica de login do Firebase
      // Por agora, vamos direto para a tela de início
      setCurrentView('start');
  }, []);

  return (
    <div className="App">
      {currentView === 'start' && <StartScreen onStart={handleStartConsultation} />}
      
      {currentView === 'consultation' && (
        <ConsultationScreen 
          userId={userId} 
          onFinish={handleFinishConsultation} 
        />
      )}
    </div>
  );
}

export default App;