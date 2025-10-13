// src/MainLayout.jsx
import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import './MainLayout.css';

// O layout agora recebe e repassa a função onLogout
const MainLayout = ({ onLogout }) => {
  return (
    <div className="main-layout">
      <Sidebar onLogout={onLogout} />
      <main className="content-area">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;