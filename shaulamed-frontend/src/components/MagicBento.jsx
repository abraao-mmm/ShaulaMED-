// MagicBento.jsx
import React, { useRef, useEffect, useCallback, useState } from "react";
import { gsap } from "gsap";
import "./MagicBento.css";

const DEFAULT_PARTICLE_COUNT = 12;
const DEFAULT_GLOW_COLOR = "132, 0, 255";

// ... (O código createParticleElement e ParticleCard permanece exatamente o mesmo) ...
const createParticleElement = (x, y, color) => {
  const el = document.createElement("div");
  el.className = "particle";
  el.style.cssText = `position: absolute; width: 4px; height: 4px; border-radius: 50%; background: rgba(${color}, 1); box-shadow: 0 0 6px rgba(${color}, 0.6); pointer-events: none; z-index: 100; left: ${x}px; top: ${y}px;`;
  return el;
};

const ParticleCard = ({ children, ...props }) => {
    const cardRef = useRef(null);
    const particlesRef = useRef([]);
    const timeoutsRef = useRef([]);
    const isHoveredRef = useRef(false);
    const memoizedParticles = useRef([]);

    const particleCount = DEFAULT_PARTICLE_COUNT;
    const glowColor = DEFAULT_GLOW_COLOR;

    const initializeParticles = useCallback(() => {
        if (!cardRef.current) return;
        const { width, height } = cardRef.current.getBoundingClientRect();
        memoizedParticles.current = Array.from({ length: particleCount }, () =>
            createParticleElement(Math.random() * width, Math.random() * height, glowColor)
        );
    }, [particleCount, glowColor]);

    const clearAllParticles = useCallback(() => {
        timeoutsRef.current.forEach(clearTimeout);
        particlesRef.current.forEach((particle) => {
            gsap.to(particle, { scale: 0, opacity: 0, duration: 0.3, onComplete: () => particle.parentNode?.removeChild(particle) });
        });
        particlesRef.current = [];
    }, []);

    const animateParticles = useCallback(() => {
        if (!cardRef.current || !isHoveredRef.current) return;
        if (memoizedParticles.current.length === 0) initializeParticles();
        memoizedParticles.current.forEach((particle, index) => {
            const timeoutId = setTimeout(() => {
                if (!isHoveredRef.current || !cardRef.current) return;
                const clone = particle.cloneNode(true);
                cardRef.current.appendChild(clone);
                particlesRef.current.push(clone);
                gsap.fromTo(clone, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3 });
                gsap.to(clone, { x: (Math.random() - 0.5) * 80, y: (Math.random() - 0.5) * 80, duration: 2 + Math.random() * 2, ease: "none", repeat: -1, yoyo: true });
                gsap.to(clone, { opacity: 0, duration: 1.5, ease: "power2.inOut", repeat: -1, yoyo: true });
            }, index * 100);
            timeoutsRef.current.push(timeoutId);
        });
    }, [initializeParticles]);

    useEffect(() => {
        const element = cardRef.current;
        if (!element) return;
        const handleMouseEnter = () => { isHoveredRef.current = true; animateParticles(); };
        const handleMouseLeave = () => { isHoveredRef.current = false; clearAllParticles(); };
        element.addEventListener("mouseenter", handleMouseEnter);
        element.addEventListener("mouseleave", handleMouseLeave);
        return () => {
            element.removeEventListener("mouseenter", handleMouseEnter);
            element.removeEventListener("mouseleave", handleMouseLeave);
            clearAllParticles();
        };
    }, [animateParticles, clearAllParticles]);

    return (
        <div ref={cardRef} {...props}>
            {children}
        </div>
    );
};


const MagicBento = ({ cardContents = {} }) => {
    
    // ===== MUDANÇA PRINCIPAL AQUI =====
    // Atualizamos o layout dos cards para a nova estrutura.
    const cardLayoutData = [
        { id: "Gravador" },       // Antigo "Insights"
        { id: "QueixaPrincipal" },// Antigo "Overview"
        { id: "Acoes" },          // Antigo "Collaboration"
        { id: "Anamnese" },       // Novo! (Parte do "Efficiency")
        { id: "Hipoteses" },      // Novo! (Parte do "Efficiency")
        { id: "ExamesSugeridos" },// Antigo "Connectivity"
        { id: "TratamentosSugeridos" }, // Antigo "Protection"
    ];
    // ==================================

    return (
        <div className="card-grid">
            {/* O card "Acoes" (Prontuário) agora é renderizado de forma diferente */}
            {cardLayoutData.filter(c => c.id !== 'Acoes').map((card) => (
                <ParticleCard key={card.id} className="card">
                    {cardContents[card.id]}
                </ParticleCard>
            ))}
            
            {/* Renderiza o card "Acoes" com uma classe especial para ocupar mais espaço */}
            <ParticleCard key="Acoes" className="card card-span-2">
                {cardContents["Acoes"]}
            </ParticleCard>
        </div>
    );
};

export default MagicBento;