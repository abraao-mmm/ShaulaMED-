import React from 'react';
// A 'motion' já não é necessária aqui, mas podemos deixar para futuras animações
import { motion } from 'framer-motion'; 
import Particles from './Particles';
import RotatingText from './RotatingText';
import './StartScreen.css';

const StartScreen = ({ onStart }) => {
  return (
    <div className="start-screen-container">
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
      
      <div className="start-screen-content">
        
        <div className="centered-content-wrapper">
          <h1 className="animated-title">
            <span className="static-text">Shaula</span>

            {/* AQUI A MUDANÇA: Voltamos para um 'div' normal e removemos as props 'layout' e 'transition' */}
            <div className="rotating-text-block">
              <RotatingText
                texts={['Med', 'Copilot']}
                // As props de animação das letras continuam as mesmas
                transition={{ type: "spring", damping: 30, stiffness: 400 }}
                initial={{ y: "100%" }}
                animate={{ y: 0 }}
                exit={{ y: "-120%" }}
                staggerDuration={0.03}
                staggerFrom="last"
                rotationInterval={2500}
                mainClassName="rotating-text-container"
                splitLevelClassName="rotating-text-wrapper"
              />
            </div>
          </h1>
          <p>Seu copiloto clínico com IA reflexiva.</p>
        </div>

        <button className="start-button" onClick={onStart}>
          Iniciar Nova Consulta
        </button>
      </div>
    </div>
  );
};

export default StartScreen;