// src/context/AuthContext.jsx
import React, { createContext, useState, useEffect, useContext } from 'react';
import { onAuthStateChanged, signInWithEmailAndPassword, setPersistence, browserSessionPersistence, browserLocalPersistence } from 'firebase/auth';
import { auth } from '../firebase/config';

const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, user => {
      setCurrentUser(user);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  // ===== NOVA FUNÇÃO DE LOGIN ADICIONADA =====
  const login = (email, password, keepLoggedIn) => {
    // Define a persistência ANTES de fazer o login
    const persistence = keepLoggedIn ? browserLocalPersistence : browserSessionPersistence;
    
    return setPersistence(auth, persistence)
      .then(() => {
        return signInWithEmailAndPassword(auth, email, password);
      });
  };
  // ===========================================

  const value = {
    currentUser,
    login // Expõe a nova função
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};