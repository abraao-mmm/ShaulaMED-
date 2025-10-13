// src/components/Sidebar.jsx

import React from 'react';
import { motion } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const menuItems = [
  { path: '/', name: 'Home' },
  { path: '/relatorios', name: 'Relatórios' },
  { path: '/perfil', name: 'Perfil' },
  { path: '/configuracoes', name: 'Configurações' },
];

const sidebarVariants = {
  hidden: { x: '-100%' },
  visible: {
    x: 0,
    transition: {
      duration: 0.5,
      ease: 'easeInOut',
      staggerChildren: 0.1, // Animação escalonada para os itens
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
};

const Sidebar = () => {
  const location = useLocation();

  return (
    <motion.nav
      className="sidebar"
      initial="hidden"
      animate="visible"
      variants={sidebarVariants}
    >
      <div className="sidebar-header">
        {/* Você pode colocar seu logo ou um ícone aqui */}
        <h3>ShaulaMed</h3>
      </div>
      <motion.ul className="sidebar-menu">
        {menuItems.map((item) => (
          <motion.li
            key={item.name}
            variants={itemVariants}
            whileHover={{ scale: 1.05, x: 5 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link
              to={item.path}
              className={`menu-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              {item.name}
            </Link>
          </motion.li>
        ))}
      </motion.ul>
    </motion.nav>
  );
};

export default Sidebar;