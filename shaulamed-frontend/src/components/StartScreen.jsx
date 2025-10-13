// src/components/StartScreen.jsx

import React from 'react';
import { motion, useMotionValue } from 'framer-motion';
import StarButton from './StarButton';
import AnimatedSubtitle from './AnimatedSubtitle';
import AnimatedText from './AnimatedText';
import AnimatedGradientText from './AnimatedGradientText';
import Particles from './Particles'; // CORREÇÃO APLICADA AQUI
import './StartScreen.css';

// Seu componente de Card interativo original
const Card = ({ children }) => {
  const cardRef = React.useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const [rotation, setRotation] = React.useState('perspective(1000px) rotateX(0deg) rotateY(0deg)');

  const handleMouseMove = React.useCallback((e) => {
    if (!cardRef.current) return;
    const { left, top, width, height } = cardRef.current.getBoundingClientRect();
    const centerX = left + width / 2;
    const centerY = top + height / 2;
    const mouseX = e.clientX;
    const mouseY = e.clientY;
    const offsetX = (mouseX - centerX) / (width / 2);
    const offsetY = (mouseY - centerY) / (height / 2);
    x.set(offsetX * 10);
    y.set(offsetY * 10);
    const rotationX = -offsetY * 5;
    const rotationY = offsetX * 5;
    setRotation(`perspective(1000px) rotateX(${rotationX}deg) rotateY(${rotationY}deg)`);
  }, [x, y]);

  const handleMouseLeave = React.useCallback(() => {
    x.set(0);
    y.set(0);
    setRotation(`perspective(1000px) rotateX(0deg) rotateY(0deg)`);
  }, [x, y]);

  return (
    <motion.div
      ref={cardRef}
      className="animated-card"
      style={{ x, y, transform: rotation }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      transition={{ type: "spring", stiffness: 100, damping: 10 }}
    >
      {children}
    </motion.div>
  );
};

// Sua tela inicial, agora com a chamada de partículas correta
const StartScreen = ({ onStart, insight }) => {
  const rotatingWords = ["intuitivo.", "inteligente.", "reflexivo.", "eficiente."];

  return (
    <div className="start-screen">
        {/* CORREÇÃO APLICADA AQUI: Usando o componente Particles diretamente */}
        <div className="particles-canvas">
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
          <Card>
            <h3 className="card-title">Curiosidade da Última Consulta</h3>
            <p className="card-insight">"{insight}"</p>
            <p className="card-tip">Passe o mouse para mais perspectiva!</p>
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