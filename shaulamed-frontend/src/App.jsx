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
  // O AppContent é um componente interno para poder usar os hooks do roteador
  const AppContent = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { currentUser } = useAuth();

    // Lógica para fazer logout
    const handleLogout = async () => {
      try {
        await signOut(auth);
        // Após o logout, o onAuthStateChanged no AuthContext irá
        // atualizar o currentUser, e o ProtectedRoute redirecionará para /login.
        // Adicionamos um navigate explícito por segurança.
        navigate('/login');
      } catch (error) {
        console.error("Erro ao fazer logout:", error);
      }
    };

    const handleStartConsultation = () => {
      navigate('/consulta');
    };

    const handleFinishConsultation = (insight) => {
      navigate('/', { state: { insight } });
    };

    // Pega o insight passado durante a navegação, se houver
    const insightFromNavigation = location.state?.insight;

    return (
      <Routes>
        {/* === ROTAS PÚBLICAS === */}
        {/* Acessíveis apenas quando o usuário NÃO está logado */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/cadastro" element={<SignupPage />} />

        {/* === ROTAS PROTEGIDAS === */}
        {/* Só são acessíveis se o usuário estiver logado */}
        <Route element={<ProtectedRoute />}>
          {/* Rotas que usam o layout principal com a barra lateral */}
          <Route element={<MainLayout onLogout={handleLogout} />}>
            <Route
              path="/"
              element={<HomePage onStart={handleStartConsultation} insight={insightFromNavigation} />}
            />
            <Route path="/relatorios" element={<ReportsPage />} />
            <Route path="/perfil" element={<ProfilePage />} />
            <Route path="/configuracoes" element={<SettingsPage />} />
          </Route>

          {/* Rota da consulta, que não usa o layout principal (tela cheia) */}
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