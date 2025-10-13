// src/components/settings/AccountPage.jsx
import React from 'react';
import './AccountPage.css'; // Renomeamos o CSS também
import PricingTiers from './PricingTiers';

const AccountPage = () => {

    const handleExportData = async () => {
        alert("Iniciando o download dos seus dados...");
        // Lógica de exportação que você já tem...
    };

    const handleDeleteAccount = () => {
        const confirmation = prompt("Esta ação é irreversível. Para confirmar, digite 'EXCLUIR MINHA CONTA'.");
        if (confirmation === "EXCLUIR MINHA CONTA") {
            alert("Funcionalidade de exclusão em desenvolvimento. Sua conta não foi excluída.");
        } else if (confirmation !== null) {
            alert("A confirmação está incorreta. Ação cancelada.");
        }
    };

  return (
    <div className="settings-section">
      {/* --- 1. SEÇÃO DE ASSINATURA --- */}
      <h2>Assinatura</h2>
      <div className="widget">
        <p className="section-subtitle">Escolha o plano que melhor se adapta à sua prática clínica.</p>
        <PricingTiers />
      </div>

      {/* --- 2. SEÇÃO PERFIL DO MÉDICO (BUILDER PROFILE) --- */}
      <h2 className="section-divider">Perfil do Médico</h2>
      <div className="widget">
        <h3>Personalize seu Perfil</h3>
        <p>Estas informações são usadas para personalizar sua experiência e documentos gerados.</p>
        <div className="profile-fields">
            <div className="form-group">
                <label>E-mail</label>
                <input type="email" value="thalles-teste@shaulamed.com" disabled />
            </div>
            {/* Adicionar outros campos de perfil aqui se desejar */}
        </div>
      </div>

      {/* --- 3. SEÇÃO DE AÇÕES DA CONTA (EXCLUIR) --- */}
      <h2 className="section-divider">Conta</h2>
       <div className="widget danger-zone">
        <div className="action-item">
          <div>
            <h4>Exportar Meus Dados</h4>
            <p>Faça o download de todos os seus dados de perfil e histórico de consultas.</p>
          </div>
          <button onClick={handleExportData} className="action-button secondary">Exportar</button>
        </div>
        <div className="action-item">
          <div>
            <h4>Excluir Conta</h4>
            <p>Esta ação apagará permanentemente sua conta e todos os dados associados.</p>
          </div>
          <button onClick={handleDeleteAccount} className="action-button danger">Excluir</button>
        </div>
      </div>
    </div>
  );
};

export default AccountPage;