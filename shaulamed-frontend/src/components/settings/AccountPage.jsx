// src/components/settings/AccountPage.jsx
import React from 'react';
import { useAuth } from '../../context/AuthContext'; // Importa o hook para pegar o usuário
import './AccountPage.css';
import PricingTiers from './PricingTiers';

const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

const AccountPage = () => {
    // Pega o usuário logado a partir do nosso contexto de autenticação
    const { currentUser } = useAuth();

    const handleExportData = async () => {
        if (!currentUser) return;
        alert("Iniciando o download dos seus dados...");
        try {
            const response = await fetch(`${API_BASE_URL}/medico/${currentUser.uid}/export-data`);
            if (!response.ok) throw new Error("Não foi possível exportar os dados.");
            const data = await response.json();
            
            const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(data, null, 2))}`;
            const link = document.createElement("a");
            link.href = jsonString;
            link.download = `shaulamed_export_${currentUser.uid}.json`;
            link.click();
        } catch (error) {
            alert(`Erro: ${error.message}`);
        }
    };
    
    const handleDeleteAccount = () => {
        if (!currentUser) return;
        const confirmation = prompt("Esta ação é irreversível e apagará todos os seus dados. Para confirmar, digite 'EXCLUIR MINHA CONTA'.");
        if (confirmation === "EXCLUIR MINHA CONTA") {
            // AQUI IRIA A LÓGICA DE CHAMADA À API PARA DELETAR A CONTA
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
                {/* Exibe o email do usuário logado dinamicamente */}
                <input type="email" value={currentUser?.email || 'Carregando...'} disabled />
            </div>
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