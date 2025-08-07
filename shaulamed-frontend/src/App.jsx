import React, { useState } from 'react';
import StartScreen from './components/StartScreen';
import MagicBento from './components/MagicBento';

// Estilos para o botão de finalizar, para não precisarmos de outro ficheiro CSS
const finishButtonStyle = {
    padding: '1rem 2rem',
    fontSize: '1rem',
    color: 'var(--white)',
    backgroundColor: '#d9534f', // Cor vermelha para indicar "finalizar"
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 0 20px rgba(217, 83, 79, 0.4)'
};

const buttonContainerStyle = {
    textAlign: 'center',
    padding: '2rem',
    backgroundColor: '#060010' // Garante que o fundo do botão seja consistente
};


function App() {
  const [currentView, setCurrentView] = useState('start'); // 'start' ou 'consultation'

  const handleStartConsultation = () => {
    console.log("Iniciando a consulta...");
    setCurrentView('consultation');
  };

  const handleFinishConsultation = () => {
    console.log("Finalizando a consulta...");
    setCurrentView('start');
  };

  if (currentView === 'start') {
    return <StartScreen onStart={handleStartConsultation} />;
  }

  if (currentView === 'consultation') {
    return (
      <div>
        <MagicBento
          textAutoHide={true}
          enableStars={true}
          enableSpotlight={true}
          enableBorderGlow={true}
          enableTilt={true}
          enableMagnetism={true}
          clickEffect={true}
          spotlightRadius={300}
          particleCount={12}
          glowColor="132, 0, 255"
        />
        <div style={buttonContainerStyle}>
            <button 
              style={finishButtonStyle}
              onClick={handleFinishConsultation}
            >
              Finalizar Sessão e Salvar
            </button>
        </div>
      </div>
    );
  }

  // Se nenhuma view corresponder, não renderiza nada (ou uma tela de erro)
  return null;
}

export default App;