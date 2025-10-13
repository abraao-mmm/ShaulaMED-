// src/App.jsx

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';

import MainLayout from './MainLayout';
import HomePage from './pages/HomePage';
import ReportsPage from './pages/ReportsPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage'; // <-- IMPORTAÇÃO QUE FALTAVA
import ConsultationScreen from './components/ConsultationScreen';

function App() {
  const [userId, setUserId] = useState('TEST_UID_THALLES');
  const [lastInsight, setLastInsight] = useState(null);

  const AppContent = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const insightFromNavigation = location.state?.insight;

    const handleStartConsultation = () => {
      navigate('/consulta');
    };

    const handleFinishConsultation = (insight) => {
      navigate('/', { state: { insight } });
    };

    return (
      <Routes>
        <Route element={<MainLayout />}>
          <Route 
            path="/" 
            element={<HomePage onStart={handleStartConsultation} insight={insightFromNavigation} />} 
          />
          <Route path="/relatorios" element={<ReportsPage />} />
          <Route path="/perfil" element={<ProfilePage />} />

          {/* ===== CORREÇÃO APLICADA AQUI ===== */}
          {/* Esta é a linha que registra a página de Configurações */}
          <Route path="/configuracoes" element={<SettingsPage />} />

        </Route>

        <Route 
          path="/consulta" 
          element={<ConsultationScreen userId={userId} onFinish={handleFinishConsultation} />} 
        />
      </Routes>
    );
  };

  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;