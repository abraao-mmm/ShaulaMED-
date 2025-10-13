// src/components/StartScreen.jsx

import React from 'react';
import { motion } from 'framer-motion';
import StarButton from './StarButton';
import AnimatedSubtitle from './AnimatedSubtitle';
import AnimatedText from './AnimatedText';
import AnimatedGradientText from './AnimatedGradientText';
import Particles from './Particles'; // <-- CORRECTION 1: Import the correct component
import './StartScreen.css';

// This is a simplified interactive card for the insight
const InsightCard = ({ children }) => {
  return (
    <motion.div
      className="animated-card"
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: 0.3, duration: 0.8, type: 'spring' }}
    >
      {children}
    </motion.div>
  );
};

const StartScreen = ({ onStart, insight }) => {
  const rotatingWords = ["intuitivo.", "inteligente.", "reflexivo.", "eficiente."];

  return (
    <div className="start-screen">
      {/* CORRECTION 2: Use the Particles component you already have */}
      <div className="particles-background">
        <Particles
            particleCount={150}
            particleSpread={8}
            speed={0.1}
            particleBaseSize={80}
            moveParticlesOnHover={true}
            alphaParticles={true}
        />
      </div>
      
      <div className="content-wrapper">
        <motion.div
          className="header-content"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
        >
          <AnimatedGradientText text="ShaulaMED" className="main-title" />
          <AnimatedText words={rotatingWords} />
          <AnimatedSubtitle text="Amplificando seu raciocínio clínico." />
        </motion.div>

        {insight && (
          <InsightCard>
            <h3 className="card-title">Curiosidade da Última Consulta</h3>
            <p className="card-insight">"{insight}"</p>
          </InsightCard>
        )}

        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: insight ? 0.5 : 1, duration: 1, ease: "easeOut" }}
          className="start-button-container"
        >
          <StarButton onClick={onStart}>
            Iniciar Nova Consulta
          </StarButton>
        </motion.div>
      </div>
    </div>
  );
};

export default StartScreen;