// src/pages/SettingsPage.jsx
import React from 'react';
import './SettingsPage.css';
// A linha abaixo é a que causa o erro se o arquivo não estiver no lugar certo.
// Ela sobe um nível ('..') de /pages para /src, entra em /components, e depois em /settings.
import AccountPage from '../components/settings/AccountPage';

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