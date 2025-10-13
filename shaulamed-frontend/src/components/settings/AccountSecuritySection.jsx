// src/components/settings/AccountSecuritySection.jsx
import React, { useState } from 'react';
import './Section.css'; // Reutiliza o CSS geral da seção

const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";
const USER_ID = "TEST_UID_THALLES"; // UID de teste

const AccountSecuritySection = () => {
  // Estado para o formulário de senha
  const [passwords, setPasswords] = useState({ current: '', new: '', confirm: '' });
  const [message, setMessage] = useState({ text: '', type: '' });

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswords(prev => ({ ...prev, [name]: value }));
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwords.new !== passwords.confirm) {
      setMessage({ text: 'A nova senha e a confirmação não coincidem.', type: 'error' });
      return;
    }
    // Lógica de chamada à API (a ser implementada com a API real)
    setMessage({ text: 'Funcionalidade de alterar senha em desenvolvimento.', type: 'info' });
    setTimeout(() => setMessage({ text: '', type: '' }), 3000);
  };

  const handleExportData = async () => {
    alert("Iniciando o download dos seus dados...");
    try {
        const response = await fetch(`${API_BASE_URL}/medico/${USER_ID}/export-data`);
        if (!response.ok) throw new Error("Não foi possível exportar os dados.");
        const data = await response.json();

        // Cria um arquivo JSON e força o download no navegador
        const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(data, null, 2))}`;
        const link = document.createElement("a");
        link.href = jsonString;
        link.download = `shaulamed_export_${USER_ID}.json`;
        link.click();

    } catch (error) {
        alert(`Erro: ${error.message}`);
    }
  };

  const handleDeleteAccount = () => {
      const confirmation = prompt("Esta ação é irreversível. Para confirmar, digite 'EXCLUIR MINHA CONTA' e sua senha na caixa abaixo, separados por vírgula (ex: EXCLUIR MINHA CONTA,sua_senha_aqui)");
      if (confirmation) {
          // Lógica de chamada à API (a ser implementada)
          alert("Funcionalidade de exclusão em desenvolvimento. Sua conta não foi excluída.");
      }
  };


  return (
    <div className="settings-section">
      <h2>Conta & Segurança</h2>

      {/* Widget para Alterar Senha */}
      <div className="widget">
        <h3>Alterar Senha</h3>
        <form onSubmit={handlePasswordSubmit} className="settings-form">
          <div className="form-group">
            <label>Senha Atual</label>
            <input type="password" name="current" value={passwords.current} onChange={handlePasswordChange} />
          </div>
          <div className="form-group">
            <label>Nova Senha</label>
            <input type="password" name="new" value={passwords.new} onChange={handlePasswordChange} />
          </div>
          <div className="form-group">
            <label>Confirmar Nova Senha</label>
            <input type="password" name="confirm" value={passwords.confirm} onChange={handlePasswordChange} />
          </div>
          <button type="submit" className="action-button">Salvar Nova Senha</button>
          {message.text && <p className={`form-message ${message.type}`}>{message.text}</p>}
        </form>
      </div>

      {/* Widget para Zona de Ações */}
      <div className="widget danger-zone">
        <h3>Zona de Ações</h3>
        <p>Estas ações são importantes e, em alguns casos, irreversíveis.</p>
        <div className="action-item">
          <div>
            <h4>Exportar Meus Dados</h4>
            <p>Faça o download de todos os seus dados de perfil e histórico de consultas em formato JSON.</p>
          </div>
          <button onClick={handleExportData} className="action-button secondary">Exportar Dados</button>
        </div>
        <div className="action-item">
          <div>
            <h4>Excluir Conta</h4>
            <p>Esta ação apagará permanentemente sua conta, seu perfil e todo o seu histórico de consultas.</p>
          </div>
          <button onClick={handleDeleteAccount} className="action-button danger">Excluir Minha Conta</button>
        </div>
      </div>
    </div>
  );
};

export default AccountSecuritySection;