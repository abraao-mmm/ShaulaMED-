// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from './context/AuthContext'; // 1. Importa o hook de autenticação
import { auth } from './firebase/config';
import { signOut } from 'firebase/auth';

// Importação dos Layouts e Páginas
import MainLayout from './MainLayout';
import ProtectedRoute from './ProtectedRoute';
import HomePage from './pages/HomePage';
import ReportsPage from './pagesS/ReportsPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';
import ConsultationScreen from './components/ConsultationScreen';
import LoginPage from './pages/auth/LoginPage';
import SignupPage from './pages/auth/SignupPage';

function App() {
  const AppContent = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { currentUser } = useAuth(); // 2. Pega o usuário que está logado

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
          
          {/* ===== 3. CORREÇÃO APLICADA AQUI ===== */}
          {/* Removemos o userId de teste e passamos o UID real do usuário logado.
            O 'currentUser?.uid' garante que só passamos o ID se o usuário existir.
          */}
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