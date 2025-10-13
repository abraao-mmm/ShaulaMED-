// src/components/LightRays.jsx

import React from 'react';
import { motion } from 'framer-motion';
import './LightRays.css';

const LightRays = () => {
  // Gera um array de 8 raios para a animação
  const rays = Array.from({ length: 8 });

  const rayVariants = {
    initial: {
      opacity: 0,
      rotate: (i) => i * 45, // Distribui os raios em 360 graus
      scale: 0.8,
    },
    animate: (i) => ({
      opacity: [0, 0.2, 0],
      scale: [0.8, 1.2, 0.8],
      transition: {
        duration: 15 + Math.random() * 10, // Duração longa e variada
        repeat: Infinity,
        delay: i * 2, // Inicia cada raio em um tempo diferente
        ease: "easeInOut",
      },
    }),
  };

  return (
    <div className="light-rays-container">
      {rays.map((_, i) => (
        <motion.div
          key={i}
          className="ray"
          custom={i}
          variants={rayVariants}
          initial="initial"
          animate="animate"
        />
      ))}
    </div>
  );
};

export default LightRays;