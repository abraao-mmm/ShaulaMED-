// src/components/settings/SubscriptionSection.jsx
import React from 'react';
import './Section.css';
import PricingTiers from './PricingTiers'; // Importa o novo componente

const SubscriptionSection = () => {
  return (
    <div className="settings-section">
      <h2>Assinatura & Faturamento</h2>
      <p className="section-subtitle">Escolha o plano que melhor se adapta à sua prática clínica.</p>
      <PricingTiers />
    </div>
  );
};

export default SubscriptionSection;