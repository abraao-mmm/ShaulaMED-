// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

import MainLayout from './MainLayout';
import HomePage from './pages/HomePage';
import ReportsPage from './pages/ReportsPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';
import ConsultationScreen from './components/ConsultationScreen';
import LoginPage from './pages/auth/LoginPage';
import SignupPage from './pages/auth/SignupPage';
import ProtectedRoute from './ProtectedRoute';

function App() {
  const AppContent = () => {
    const navigate = useNavigate();
    const { currentUser } = useAuth(); // Pega o usuário do nosso contexto

    const handleStartConsultation = () => {
      navigate('/consulta');
    };

    const handleFinishConsultation = (insight) => {
      navigate('/', { state: { insight } });
    };

    return (
      <Routes>
        {/* Rotas Públicas */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/cadastro" element={<SignupPage />} />

        {/* Rotas Protegidas */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route
              path="/"
              element={<HomePage onStart={handleStartConsultation} />}
            />
            <Route path="/relatorios" element={<ReportsPage />} />
            <Route path="/perfil" element={<ProfilePage />} />
            <Route path="/configuracoes" element={<SettingsPage />} />
          </Route>
          <Route
            path="/consulta"
            element={<ConsultationScreen userId={currentUser?.uid} onFinish={handleFinishConsultation} />}
          />
        </Route>
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