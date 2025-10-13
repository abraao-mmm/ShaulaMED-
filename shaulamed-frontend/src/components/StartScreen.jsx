// src/components/StartScreen.jsx

import React from 'react';
import { motion, useMotionValue } from 'framer-motion';
import StarButton from './StarButton';
import AnimatedSubtitle from './AnimatedSubtitle';
import AnimatedText from './AnimatedText';
import AnimatedGradientText from './AnimatedGradientText';
import Particles from './Particles'; // <-- AQUI ESTÁ A IMPORTAÇÃO CORRETA
import './StartScreen.css';

// Seu componente Card interativo, robusto e original.
const Card = ({ children }) => {
  const cardRef = React.useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const handleMouseMove = (e) => {
    if (!cardRef.current) return;
    const { left, top, width, height } = cardRef.current.getBoundingClientRect();
    const mouseX = e.clientX - left;
    const mouseY = e.clientY - top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;
    x.set(xPct * 30); // Sensibilidade do efeito parallax
    y.set(yPct * 30);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={cardRef}
      className="animated-card"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateY: useMotionValue(0), // Inicializando para evitar erros
        rotateX: useMotionValue(0), // Inicializando para evitar erros
        transformStyle: 'preserve-3d',
      }}
      // Animação de entrada para o card
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
    >
      <motion.div
        style={{
          x,
          y,
          transformStyle: 'preserve-3d',
        }}
        className="card-content-wrapper"
      >
        {children}
      </motion.div>
    </motion.div>
  );
};


const StartScreen = ({ onStart, insight }) => {
  const rotatingWords = ["intuitivo.", "inteligente.", "reflexivo.", "eficiente."];

  return (
    <div className="start-screen">
      {/* Usando seu componente Particles.jsx original */}
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

        {/* O Card para o Insight só aparece se a prop 'insight' existir */}
        {insight && (
          <Card>
            <h3 className="card-title">Curiosidade da Última Consulta</h3>
            <p className="card-insight">"{insight}"</p>
            <p className="card-tip">Passe o mouse para sentir o efeito!</p>
          </Card>
        )}

        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 1, ease: "easeOut" }}
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