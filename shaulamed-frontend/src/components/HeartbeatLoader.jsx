import React, { useEffect, useRef } from 'react';
// Esta importação está correta e é a mais segura.
import * as anime from 'animejs';
import './HeartbeatLoader.css';

const HeartbeatLoader = () => {
    const pathRef = useRef(null);

    useEffect(() => {
        const path = pathRef.current;
        if (!path) return;

        // ===== A CORREÇÃO FINAL ESTÁ AQUI =====
        // Acessamos a função 'timeline' diretamente do objeto 'anime', sem o '.default'.
        const heartbeatAnimation = anime.timeline({
            loop: true,
            direction: 'alternate',
            duration: 500,
        }).add({
            targets: path,
            d: 'M 0 50 C 10 50, 15 20, 20 50 C 25 80, 30 50, 35 50 C 40 20, 45 80, 50 50 C 55 20, 60 80, 65 50 C 70 20, 75 80, 80 50 C 85 20, 90 50, 100 50',
            easing: 'easeInOutQuad'
        }).add({
            targets: path,
            d: 'M 0 50 C 10 50, 15 80, 20 50 C 25 20, 30 50, 35 50 C 40 80, 45 20, 50 50 C 55 80, 60 20, 65 50 C 70 80, 75 20, 80 50 C 85 80, 90 50, 100 50',
            easing: 'easeInOutQuad'
        });

        // Cleanup function to pause animation when component unmounts
        return () => {
            if (heartbeatAnimation) {
                heartbeatAnimation.pause();
            }
        };
    }, []);

    return (
        <div className="heartbeat-loader-container">
            <svg id="progress" viewBox="0 0 100 100" width="150" height="150">
                <g fill="none" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" transform="translate(5 5) scale(0.9 0.9)">
                    <path stroke="var(--border-color)" opacity="0.5" d="M 0 50, 100 50"></path>
                    <path ref={pathRef} stroke="var(--purple-primary)" d="M 0 50, 100 50"></path>
                </g>
            </svg>
        </div>
    );
};

export default HeartbeatLoader;