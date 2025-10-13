// src/pages/SettingsPage.jsx
import React from 'react';
import './SettingsPage.css';
import AccountPage from '../components/settings/AccountPage'; // Importa a nova página unificada

const SettingsPage = () => {
  return (
    <div className="settings-page-container">
        <div className="settings-header">
            <h1>Configurações</h1>
        </div>
        <div className="settings-content-area">
            <AccountPage />
        </div>
    </div>
  );
};

export default SettingsPage;