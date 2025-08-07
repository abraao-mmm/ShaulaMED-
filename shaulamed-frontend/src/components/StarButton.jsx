import React from 'react';
import './StarButton.css';

// Para evitar repetir o código SVG gigante 6 vezes, criamos um pequeno componente para ele.
const StarIcon = () => (
  <svg xmlnsXlink="http://www.w3.org/1999/xlink" viewBox="0 0 784.11 815.53" className="star-svg" version="1.1" xmlSpace="preserve" xmlns="http://www.w3.org/2000/svg">
    <g>
      <path d="M392.05 0c-20.9,210.08 -184.06,378.41 -392.05,407.78 207.96,29.37 371.12,197.68 392.05,407.74 20.93,-210.06 184.09,-378.37 392.05,-407.74 -207.98,-29.38 -371.16,-197.69 -392.06,-407.78z" className="fil0"></path>
    </g>
  </svg>
);

const StarButton = ({ onClick, children }) => {
  return (
    <button className="star-btn" onClick={onClick}>
      {children}
      <div className="star-1"><StarIcon /></div>
      <div className="star-2"><StarIcon /></div>
      <div className="star-3"><StarIcon /></div>
      <div className="star-4"><StarIcon /></div>
      <div className="star-5"><StarIcon /></div>
      <div className="star-6"><StarIcon /></div>
    </button>
  );
};

export default StarButton;