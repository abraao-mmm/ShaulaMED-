// src/components/AnimatedText.jsx

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './AnimatedText.css';

const AnimatedText = ({ words }) => {
  const [index, setIndex] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % words.length);
    }, 2500); // Muda a palavra a cada 2.5 segundos

    return () => clearInterval(interval);
  }, [words.length]);

  const variants = {
    enter: {
      y: 20,
      opacity: 0,
    },
    center: {
      zIndex: 1,
      y: 0,
      opacity: 1,
    },
    exit: {
      zIndex: 0,
      y: -20,
      opacity: 0,
    },
  };

  return (
    <div className="animated-text-container">
      <AnimatePresence initial={false} mode="wait">
        <motion.span
          className="animated-text-word"
          key={index}
          variants={variants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{
            y: { type: 'spring', stiffness: 300, damping: 20 },
            opacity: { duration: 0.5 },
          }}
        >
          {words[index]}
        </motion.span>
      </AnimatePresence>
    </div>
  );
};

export default AnimatedText;