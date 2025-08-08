import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import './HeartbeatLoader.css';

// ===== AS NOVAS FORMAS DO BATIMENTO CARDÍACO ESTÃO AQUI =====
// Estas strings de 'path' desenham um traçado de EKG mais realista
const heartbeatPath1 = "M0,50 L20,50 L25,40 L30,50 L35,50 L42,20 L50,70 L58,30 L65,50 L80,50 L85,45 L90,50 L100,50";
const heartbeatPath2 = "M0,50 L20,50 L25,45 L30,50 L35,50 L42,30 L50,60 L58,40 L65,50 L80,50 L85,48 L90,50 L100,50";

const HeartbeatLoader = () => {
    return (
        <div className="heartbeat-loader-container">
            <svg id="progress" viewBox="0 0 100 100" width="150" height="150">
                <g fill="none" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" transform="translate(5 5) scale(0.9 0.9)">
                    {/* Linha de base cinzenta e estática */}
                    <path stroke="var(--border-color)" opacity="0.5" d="M 0 50, 100 50"></path>
                    
                    {/* O nosso caminho animado com a forma correta */}
                    <motion.path 
                        stroke="var(--purple-primary)" 
                        d={heartbeatPath1} // Estado inicial do caminho
                        animate={{
                            // Anima a propriedade 'd' (a forma) entre os dois estados do batimento
                            d: [heartbeatPath1, heartbeatPath2, heartbeatPath1]
                        }}
                        transition={{
                            duration: 1.2, // Um pouco mais lento para um ritmo mais natural
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                    />
                </g>
            </svg>
        </div>
    );
};

export default HeartbeatLoader;