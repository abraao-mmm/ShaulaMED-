import React from 'react';
import { motion } from 'framer-motion';
import Particles from './Particles';
import RotatingText from './RotatingText';
import AnimatedSubtitle from './AnimatedSubtitle';
import StarButton from './StarButton';
import './StartScreen.css';

const StartScreen = ({ onStart, insight }) => {
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
            <motion.div
              className="rotating-text-block"
              layout
              transition={{ type: "spring", damping: 20, stiffness: 200 }}
            >
              <RotatingText
                texts={['Med', 'Copilot']}
                initial={{ y: "100%" }}
                animate={{ y: 0 }}
                exit={{ y: "-120%" }}
                staggerDuration={0.03}
                staggerFrom="last"
                rotationInterval={2500}
                mainClassName="rotating-text-container"
                splitLevelClassName="rotating-text-wrapper"
              />
            </motion.div>
          </h1>
          <AnimatedSubtitle text="Amplificando seu raciocínio clínico." />
        </div>
        <div className="start-button-wrapper">
            <StarButton onClick={onStart}>
                Iniciar Nova Consulta
            </StarButton>
        </div>
      </div>
    </div>
  );
};

export default StartScreen;