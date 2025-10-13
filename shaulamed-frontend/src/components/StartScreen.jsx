import React, { useRef, useEffect, useState, useCallback } from 'react';
import { motion, useScroll, useTransform, useMotionValue } from 'framer-motion';
import StarButton from './StarButton';
import AnimatedSubtitle from './AnimatedSubtitle';
import AnimatedText from './AnimatedText'; // Certifique-se de que este componente existe e funciona
import AnimatedGradientText from './AnimatedGradientText'; // Para o título ShaulaMED
import './StartScreen.css';
import initParticles from '../utils/particles'; // Certifique-se que o caminho está correto

const Card = ({ children }) => {
  const cardRef = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const [rotation, setRotation] = useState(0);

  const handleMouseMove = useCallback((e) => {
    if (!cardRef.current) return;

    const { left, top, width, height } = cardRef.current.getBoundingClientRect();
    const centerX = left + width / 2;
    const centerY = top + height / 2;

    const mouseX = e.clientX;
    const mouseY = e.clientY;

    const offsetX = (mouseX - centerX) / (width / 2); // -1 to 1
    const offsetY = (mouseY - centerY) / (height / 2); // -1 to 1

    x.set(offsetX * 10); // Adjust sensitivity
    y.set(offsetY * 10); // Adjust sensitivity

    // Calculate rotation based on cursor position relative to center
    const rotationX = -offsetY * 5; // Rotate less on X
    const rotationY = offsetX * 5;  // Rotate less on Y
    setRotation(`perspective(1000px) rotateX(${rotationX}deg) rotateY(${rotationY}deg)`);

  }, [x, y]);

  const handleMouseLeave = useCallback(() => {
    x.set(0);
    y.set(0);
    setRotation(`perspective(1000px) rotateX(0deg) rotateY(0deg)`);
  }, [x, y]);

  return (
    <motion.div
      ref={cardRef}
      className="animated-card"
      style={{ x, y, transform: rotation }} // Use 'transform' for rotation
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      transition={{ type: "spring", stiffness: 100, damping: 10 }}
    >
      {children}
    </motion.div>
  );
};


const StartScreen = ({ onStart, insight }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    let cleanup;
    if (canvasRef.current) {
      cleanup = initParticles(canvasRef.current);
    }
    return () => cleanup && cleanup();
  }, []);

  // Palavras para o efeito de texto rotativo
  const rotatingWords = ["intuitivo.", "inteligente.", "reflexivo.", "eficiente."];

  return (
    <div className="start-screen">
      <canvas ref={canvasRef} className="particles-canvas"></canvas>
      <div className="content-wrapper">
        <motion.div
          className="header-content"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
        >
          {/* O título ShaulaMED agora é um AnimatedGradientText */}
          <AnimatedGradientText text="ShaulaMED" className="main-title" />
          <AnimatedText words={rotatingWords} /> {/* Componente para o texto rotativo */}
          <AnimatedSubtitle text="Amplificando seu raciocínio clínico." />
        </motion.div>

        {/* Novo Card para o Insight */}
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