import React from 'react';
import { motion } from 'framer-motion';
import './AnimatedGradientText.css'; // Crie este arquivo CSS

const AnimatedGradientText = ({ text, className }) => {
  return (
    <motion.h1
      className={`animated-gradient-text ${className}`}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      {text}
    </motion.h1>
  );
};

export default AnimatedGradientText;