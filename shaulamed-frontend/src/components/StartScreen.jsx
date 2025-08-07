import React from 'react';
import './StartScreen.css'; // Criaremos este CSS a seguir

const StartScreen = ({ onStart }) => {
  return (
    <div className="start-screen">
      <h1>ShaulaMed Copilot</h1>
      <p>Seu copiloto clínico com IA reflexiva.</p>
      <button className="start-button" onClick={onStart}>
        Iniciar Nova Consulta
      </button>
    </div>
  );
};

export default StartScreen;