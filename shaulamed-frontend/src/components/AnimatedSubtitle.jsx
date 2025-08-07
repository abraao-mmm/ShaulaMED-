import React, { useEffect, useRef } from 'react';
import './AnimatedSubtitle.css';

// ===== FUNÇÃO DE COR ALTERADA =====
// Em vez de cores totalmente aleatórias, vamos escolher tons de roxo
const getRandomPurpleShade = () => {
    const purpleShades = ['#d8b4fe', '#c084fc', '#a855f7', '#9333ea', '#7e22ce', '#efdffc'];
    return purpleShades[Math.floor(Math.random() * purpleShades.length)];
};

const AnimatedSubtitle = ({ text }) => {
    const letterRefs = useRef([]);
    const words = text.split(' ');

    useEffect(() => {
        let whichLetter = 0;
        const trailAmount = 7;
        const letterElements = letterRefs.current;
        const totalLetters = letterElements.length;

        if (totalLetters === 0) return;

        const intervalId = setInterval(() => {
            if (whichLetter < totalLetters + trailAmount) {
                // Limpa a letra que está para trás no "rasto" de luz
                const letterToClearIndex = whichLetter - trailAmount;
                if (letterToClearIndex >= 0 && letterToClearIndex < totalLetters) {
                    // Volta à cor e sombra de base (o brilho do CSS)
                    letterElements[letterToClearIndex].style.color = 'whitesmoke';
                    letterElements[letterToClearIndex].style.textShadow = ''; // Remove a sombra extra
                }

                // Acende a letra atual com um tom de roxo
                const letterToLightIndex = whichLetter;
                if (letterToLightIndex < totalLetters) {
                    const rColor = getRandomPurpleShade(); // Usa a nova função
                    const tColor = getRandomPurpleShade(); // Usa a nova função
                    letterElements[letterToLightIndex].style.color = rColor;
                    // Adiciona uma sombra extra e mais forte à letra atual
                    letterElements[letterToLightIndex].style.textShadow = `0px 0px 15px ${tColor}, 0 0 25px ${tColor}`;
                }
                
                whichLetter++;
            } else {
                whichLetter = 0;
            }
        }, 75);

        return () => clearInterval(intervalId);

    }, [text]);

    let letterIndex = -1;
    return (
        <div className="animated-subtitle-container">
            {words.map((word, wordIdx) => (
                <div key={wordIdx} className="textSec">
                    {word.split('').map((char, charIdx) => {
                        letterIndex++;
                        const currentLetterIndex = letterIndex;
                        return (
                            <span 
                                key={charIdx} 
                                className="text"
                                ref={el => letterRefs.current[currentLetterIndex] = el}
                            >
                                {char}
                            </span>
                        );
                    })}
                </div>
            ))}
        </div>
    );
};

export default AnimatedSubtitle;