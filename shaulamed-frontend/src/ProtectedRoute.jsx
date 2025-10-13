// src/ProtectedRoute.jsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

const ProtectedRoute = () => {
  const { currentUser } = useAuth();

  // Se não há usuário logado, redireciona para a página de login
  if (!currentUser) {
    return <Navigate to="/login" />;
  }

  // Se houver usuário, renderiza o conteúdo da rota (ex: MainLayout)
  return <Outlet />;
};

export default ProtectedRoute;