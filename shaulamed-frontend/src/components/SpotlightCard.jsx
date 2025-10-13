// src/components/SpotlightCard.jsx

import React, { useRef } from 'react';
import './SpotlightCard.css';

const SpotlightCard = ({ title, value }) => {
  const cardRef = useRef(null);

  const handleMouseMove = (e) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    cardRef.current.style.setProperty('--mouse-x', `${x}px`);
    cardRef.current.style.setProperty('--mouse-y', `${y}px`);
  };

  return (
    <div
      ref={cardRef}
      className="spotlight-card"
      onMouseMove={handleMouseMove}
    >
      <div className="card-content">
        <h4 className="card-title">{title}</h4>
        <p className="card-value">{value}</p>
      </div>
      {/* O brilho é controlado pelo pseudo-elemento ::before no CSS */}
    </div>
  );
};

export default SpotlightCard;