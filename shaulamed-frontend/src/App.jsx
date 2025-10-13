// src/App.jsx

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';

import MainLayout from './MainLayout';
import HomePage from './pages/HomePage';
import ReportsPage from './pages/ReportsPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';
import ConsultationScreen from './components/ConsultationScreen';

function App() {
  const [userId, setUserId] = useState('TEST_UID_THALLES');
  const [lastInsight, setLastInsight] = useState(null);

  // Usaremos um componente wrapper para acessar os hooks do roteador
  const AppContent = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // O insight é passado via state da navegação
    const insightFromNavigation = location.state?.insight;

    const handleStartConsultation = () => {
      navigate('/consulta');
    };

    const handleFinishConsultation = (insight) => {
      // Navega de volta para a Home, passando o insight
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
          <Route path="/configuracoes" element={<SettingsPage />} />
        </Route>

        {/* A tela de consulta fica fora do layout principal */}
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