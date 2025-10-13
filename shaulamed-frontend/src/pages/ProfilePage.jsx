// src/pages/ProfilePage.jsx
import React, { useState, useEffect } from 'react';
import './ProfilePage.css';

const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";
const USER_ID = "TEST_UID_THALLES"; // UID de teste

const ProfilePage = () => {
  const [profileData, setProfileData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/medico/${USER_ID}/perfil`);
        if (!response.ok) {
          throw new Error('Falha ao buscar os dados do perfil.');
        }
        const data = await response.json();
        setProfileData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProfileData();
  }, []);

  const handleProfileUpdate = (updatedData) => {
    // Atualiza o estado local para refletir a mudança imediatamente
    setProfileData(prevData => ({ ...prevData, ...updatedData }));
  };

  if (isLoading) return <div className="loading-state">Carregando Perfil...</div>;
  if (error) return <div className="error-state">Erro: {error}</div>;

  return (
    <div className="profile-page">
      <h1>Seu Perfil</h1>
      <div className="profile-grid">
        <ProfileForm initialData={profileData} onProfileUpdate={handleProfileUpdate} />
        <ClinicalStyleWidget styleData={profileData?.estilo_clinico_observado} />
      </div>
    </div>
  );
};

// Componente para o formulário de edição
const ProfileForm = ({ initialData, onProfileUpdate }) => {
    const [formData, setFormData] = useState(initialData);
    const [isSaving, setIsSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({...prev, [name]: value}));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSaving(true);
        setSaveMessage('');
        try {
            const response = await fetch(`${API_BASE_URL}/medico/${USER_ID}/perfil`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            if (!response.ok) throw new Error('Falha ao salvar.');
            setSaveMessage('Perfil salvo com sucesso!');
            onProfileUpdate(formData); // Notifica o componente pai sobre a atualização
        } catch (err) {
            setSaveMessage('Erro ao salvar o perfil.');
        } finally {
            setIsSaving(false);
            setTimeout(() => setSaveMessage(''), 3000); // Limpa a mensagem após 3s
        }
    };

    return (
        <form className="profile-widget" onSubmit={handleSubmit}>
            <h2>Informações Profissionais</h2>
            <div className="form-group">
                <label>Nome Completo</label>
                <input type="text" name="nome_completo" value={formData.nome_completo || ''} onChange={handleChange} />
            </div>
            <div className="form-group">
                <label>Apelido (para a IA)</label>
                <input type="text" name="apelido" value={formData.apelido || ''} onChange={handleChange} />
            </div>
            <div className="form-group">
                <label>CRM</label>
                <input type="text" name="crm" value={formData.crm || ''} onChange={handleChange} />
            </div>
            <div className="form-group">
                <label>Especialidade</label>
                <input type="text" name="especialidade" value={formData.especialidade || ''} onChange={handleChange} />
            </div>
            <div className="form-group">
                <label>Email</label>
                <input type="email" value={formData.email || ''} disabled />
            </div>
            <button type="submit" disabled={isSaving}>{isSaving ? 'Salvando...' : 'Salvar Alterações'}</button>
            {saveMessage && <p className="save-message">{saveMessage}</p>}
        </form>
    );
};

// Componente para a visualização do estilo clínico
const ClinicalStyleWidget = ({ styleData }) => {
    const prescriptions = styleData?.padrao_prescritivo || {};

    return (
        <div className="profile-widget">
            <h2>Seu Estilo Clínico (Visto pela IA)</h2>
            <div className="style-section">
                <h3>Vademecum Pessoal</h3>
                {Object.keys(prescriptions).length > 0 ? (
                    <ul className="prescription-list">
                        {Object.entries(prescriptions).map(([diag, cond]) => (
                            <li key={diag}>
                                <strong>Para {diag}:</strong>
                                <p>"{cond}"</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="empty-state">A IA ainda está aprendendo suas condutas mais comuns. Continue usando o ShaulaMed!</p>
                )}
            </div>
        </div>
    );
};

export default ProfilePage;