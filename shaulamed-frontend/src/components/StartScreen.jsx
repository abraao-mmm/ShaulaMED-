import React from 'react';
import Particles from './Particles'; // Importamos o novo componente
import './StartScreen.css';

const StartScreen = ({ onStart }) => {
  return (
    <div className="start-screen-container">
      {/* O componente de partículas agora serve como fundo */}
      <div className="particle-background">
         <Particles
            particleColors={['#ffffff', '#ffffff']}
            particleCount={200}
            particleSpread={10}
            speed={0.1}
            particleBaseSize={100}
            moveParticlesOnHover={true}
            alphaParticles={false}
            disableRotation={false}
        />
      </div>

      {/* O conteúdo fica numa camada por cima */}
      <div className="start-screen-content">
        <h1>ShaulaMed Copilot</h1>
        <p>Seu copiloto clínico com IA reflexiva.</p>
        <button className="start-button" onClick={onStart}>
          Iniciar Nova Consulta
        </button>
      </div>
    </div>
  );
};

export default StartScreen;