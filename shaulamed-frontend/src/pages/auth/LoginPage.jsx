// src/pages/auth/LoginPage.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext'; // Importa nosso hook

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [keepLoggedIn, setKeepLoggedIn] = useState(false); // Estado para o checkbox
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth(); // Pega a nova função de login do contexto

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      // Usa a nossa função de login personalizada
      await login(email, password, keepLoggedIn); 
      navigate('/');
    } catch (err) {
      setError('Email ou senha inválidos. Tente novamente.');
    }
  };

  return (
    <div className="login">
      <form onSubmit={handleLogin} className="login__form">
        <h1 className="login__title">ShaulaMed</h1>
        {error && <p className="form-error-message">{error}</p>}

        <div className="login__content">
          {/* ... (bloco do email permanece o mesmo) ... */}
          <div className="login__box">
            <i className="ri-user-3-line login__icon"></i>
            <div className="login__box-input">
              <input type="email" required className="login__input" id="login-email-input" placeholder=" " value={email} onChange={(e) => setEmail(e.target.value)} />
              <label htmlFor="login-email-input" className="login__label">Email</label>
            </div>
          </div>
          {/* ... (bloco da senha permanece o mesmo) ... */}
          <div className="login__box">
            <i className="ri-lock-2-line login__icon"></i>
            <div className="login__box-input">
              <input type={showPassword ? "text" : "password"} required className="login__input" id="login-password-input" placeholder=" " value={password} onChange={(e) => setPassword(e.target.value)} />
              <label htmlFor="login-password-input" className="login__label">Senha</label>
              <i className={showPassword ? 'ri-eye-line login__eye' : 'ri-eye-off-line login__eye'} onClick={() => setShowPassword(!showPassword)}></i>
            </div>
          </div>
        </div>

        {/* ===== NOVO CHECKBOX ADICIONADO ===== */}
        <div className="login__check">
          <input 
            type="checkbox" 
            className="login__check-input" 
            id="login-check" 
            checked={keepLoggedIn} 
            onChange={(e) => setKeepLoggedIn(e.target.checked)} 
          />
          <label htmlFor="login-check" className="login__check-label">Manter conectado</label>
        </div>
        {/* ==================================== */}

        <button type="submit" className="login__button">Entrar</button>

        <p className="login__register">
          Não tem uma conta? <Link to="/cadastro">Registe-se</Link>
        </p>
      </form>
    </div>
  );
};

export default LoginPage;