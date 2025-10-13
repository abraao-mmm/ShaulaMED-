// src/MainLayout.jsx

import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import './MainLayout.css';

const MainLayout = () => {
  return (
    <div className="main-layout">
      <Sidebar />
      <main className="content-area">
        <Outlet /> {/* As páginas serão renderizadas aqui */}
      </main>
    </div>
  );
};

export default MainLayout;