// src/components/settings/SubscriptionSection.jsx
import React from 'react';
import './Section.css'; // Usaremos um CSS compartilhado

const SubscriptionSection = () => {
  // No futuro, a informação do plano virá da API
  const userPlan = {
    name: 'Plano de Teste',
    daysLeft: 21,
    isPro: false,
  };

  return (
    <div className="settings-section">
      <h2>Assinatura & Faturamento</h2>
      <div className="widget">
        <h3>Seu Plano Atual</h3>
        <p className="plan-name">{userPlan.name}</p>
        {!userPlan.isPro && (
          <p>Você possui {userPlan.daysLeft} dias restantes de teste gratuito.</p>
        )}
        <button className="upgrade-button">
          {userPlan.isPro ? 'Gerenciar Assinatura' : 'Fazer Upgrade para o PRO'}
        </button>
        <p className="widget-footer">O gerenciamento de pagamentos é feito em um ambiente seguro.</p>
      </div>
    </div>
  );
};

export default SubscriptionSection;