import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import './AnimatedInfoList.css';

const AnimatedInfoList = ({ items }) => {
    const containerRef = useRef(null);

    useEffect(() => {
        const container = containerRef.current;
        if (!container || !items || items.length === 0) return;

        const projectItems = container.querySelectorAll(".project-item");
        gsap.set(projectItems, { opacity: 0 }); // Garante que os itens começam invisíveis

        const timeline = gsap.timeline();

        // Animação de entrada, agora sem o header
        timeline.to(projectItems, {
            opacity: 1,
            duration: 0.2,
            stagger: 0.1,
            ease: "power2.out"
        });

        timeline.to(projectItems, {
            color: "#fff",
            duration: 0.2,
            stagger: 0.1,
            ease: "power2.inOut"
        }, "-=0.3");

    }, [items]);

    if (!items || items.length === 0) {
        return <p className="placeholder-text">Aguardando informações...</p>;
    }

    return (
        <div className="projects-container" ref={containerRef}>
            {/* O CABEÇALHO FOI REMOVIDO DAQUI */}

            {items.map((item, index) => (
                // Renderiza apenas as linhas de informação
                <div className="project-item" key={index}>
                    <div className="project-name">{item.label}</div>
                    <div className="project-director">{item.value || '...'}</div>
                </div>
            ))}
        </div>
    );
};

export default AnimatedInfoList;