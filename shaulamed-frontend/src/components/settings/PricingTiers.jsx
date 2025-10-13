// src/components/settings/PricingTiers.jsx
import React from 'react';
import './PricingTiers.css';

// Ícone de checkmark para a lista de funcionalidades
const CheckIcon = () => (
  <svg className="check-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
  </svg>
);

const PricingTiers = () => {
  // Definimos os dados dos planos aqui para facilitar a manutenção
  const plans = [
    {
      name: 'Essencial',
      price: 'Grátis',
      description: 'Experimente a transcrição e estruturação inteligente.',
      features: [
        '15 Consultas/mês',
        'Estruturação da Nota Clínica',
        'Geração de Atestados e Pedidos de Exame',
        'Histórico dos últimos 7 dias',
      ],
      isCurrent: true, // Indica que este é o plano atual do usuário
    },
    {
      name: 'PRO',
      price: 'R$ 89,90',
      pricePeriod: '/mês',
      description: 'A experiência completa do Copiloto Clínico Reflexivo.',
      features: [
        'Consultas Ilimitadas',
        'Painel de Relatórios Completo com IA Coach',
        'Análise de Estilo Clínico no seu Perfil',
        'Geração de todos os documentos',
        'Histórico Completo de Consultas',
      ],
      isPopular: true,
    },
  ];

  return (
    <div className="pricing-container">
      {plans.map((plan, index) => (
        <div key={index} className={`pricing-card ${plan.isPopular ? 'popular' : ''}`}>
          {plan.isPopular && <div className="popular-badge">MAIS POPULAR</div>}
          <div className="card-header">
            <h3 className="plan-name">{plan.name}</h3>
            <p className="plan-price">
              {plan.price}
              {plan.pricePeriod && <span className="price-period">{plan.pricePeriod}</span>}
            </p>
            <p className="plan-description">{plan.description}</p>
          </div>
          <ul className="features-list">
            {plan.features.map((feature, fIndex) => (
              <li key={fIndex}>
                <CheckIcon />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
          <div className="card-footer">
            <button className={`cta-button ${plan.isCurrent ? 'current-plan' : ''}`}>
              {plan.isCurrent ? 'Seu Plano Atual' : 'Fazer Upgrade'}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PricingTiers;