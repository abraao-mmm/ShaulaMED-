// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import { auth } from './firebase/config';
import { signOut } from 'firebase/auth';

// Importação dos Layouts e Páginas
import MainLayout from './MainLayout';
import ProtectedRoute from './ProtectedRoute';
import HomePage from './pages/HomePage';
import ReportsPage from './pages/ReportsPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';
import ConsultationScreen from './components/ConsultationScreen';
import LoginPage from './pages/auth/LoginPage';
import SignupPage from './pages/auth/SignupPage';

function App() {
  const AppContent = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { currentUser } = useAuth(); // Pega o usuário logado

    const handleLogout = async () => {
      await signOut(auth);
      navigate('/login');
    };

    const handleStartConsultation = () => navigate('/consulta');
    const handleFinishConsultation = (insight) => navigate('/', { state: { insight } });
    const insightFromNavigation = location.state?.insight;

    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/cadastro" element={<SignupPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout onLogout={handleLogout} />}>
            <Route path="/" element={<HomePage onStart={handleStartConsultation} insight={insightFromNavigation} />} />
            <Route path="/relatorios" element={<ReportsPage />} />
            <Route path="/perfil" element={<ProfilePage />} />
            <Route path="/configuracoes" element={<SettingsPage />} />
          </Route>
          
          {/* ===== CORREÇÃO APLICADA AQUI ===== */}
          {/* Passa o UID real do usuário logado para a tela de consulta */}
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