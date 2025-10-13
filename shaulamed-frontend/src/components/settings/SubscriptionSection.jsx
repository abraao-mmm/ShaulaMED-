// src/components/settings/SubscriptionSection.jsx
import React from 'react';
import './Section.css'; // Usaremos um CSS compartilhado

const SubscriptionSection = () => {
  // No futuro, a informação do plano virá da API via props.
  // Por enquanto, simulamos os dois estados para construir a UI.
  const isPro = false; // Mude para `true` para ver o visual do plano PRO

  // O que será exibido se o usuário for PRO
  const ProTierView = () => (
    <div className="widget">
      <h3>Seu Plano Atual</h3>
      <p className="plan-name">Plano PRO</p>
      <p>Você tem acesso a todas as funcionalidades avançadas do ShaulaMed.</p>
      <button className="manage-button">
        Gerenciar Assinatura
      </button>
      <p className="widget-footer">Você será redirecionado para nosso portal de pagamentos seguro.</p>
    </div>
  );

  // O que será exibido se o usuário estiver no plano gratuito/teste
  const FreeTierView = () => (
    <div className="widget">
      <h3>Seu Plano Atual</h3>
      <p className="plan-name">Plano Essencial (Teste)</p>
      <p>Desbloqueie o poder do Painel Reflexivo e consultas ilimitadas.</p>
      <ul className="pro-features">
        <li>✅ Consultas Ilimitadas</li>
        <li>✅ Painel de Relatórios Completo</li>
        <li>✅ Análise de Estilo Clínico</li>
      </ul>
      <button className="upgrade-button">
        Fazer Upgrade para o PRO - R$ 89,90/mês
      </button>
    </div>
  );

  return (
    <div className="settings-section">
      <h2>Assinatura & Faturamento</h2>
      {isPro ? <ProTierView /> : <FreeTierView />}
    </div>
  );
};

export default SubscriptionSection;