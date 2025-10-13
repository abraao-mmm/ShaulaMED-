// src/pages/SettingsPage.jsx

import React, { useState } from 'react';
import './SettingsPage.css';

// Vamos importar os componentes de cada seção (que criaremos a seguir)
import SubscriptionSection from '../components/settings/SubscriptionSection';
import AccountSecuritySection from '../components/settings/AccountSecuritySection';
import GeneralSection from '../components/settings/GeneralSection';
import NotificationsSection from '../components/settings/NotificationsSection';

const SettingsPage = () => {
  const [activeSection, setActiveSection] = useState('assinatura');

  const renderSection = () => {
    switch (activeSection) {
      case 'assinatura':
        return <SubscriptionSection profileData={profileData} />;
      case 'seguranca':
        return <AccountSecuritySection />;
      case 'geral':
        return <GeneralSection />;
      case 'notificacoes':
        return <NotificationsSection />;
      default:
        return <SubscriptionSection />;
    }
  };

  return (
    <div className="settings-page">
      <nav className="settings-nav">
        <button
          onClick={() => setActiveSection('assinatura')}
          className={activeSection === 'assinatura' ? 'active' : ''}
        >
          Assinatura & Faturamento
        </button>
        <button
          onClick={() => setActiveSection('seguranca')}
          className={activeSection === 'seguranca' ? 'active' : ''}
        >
          Conta & Segurança
        </button>
        <button
          onClick={() => setActiveSection('geral')}
          className={activeSection === 'geral' ? 'active' : ''}
        >
          Geral
        </button>
        <button
          onClick={() => setActiveSection('notificacoes')}
          className={activeSection === 'notificacoes' ? 'active' : ''}
        >
          Notificações
        </button>
      </nav>
      <main className="settings-content">
        {renderSection()}
      </main>
    </div>
  );
};

export default SettingsPage;