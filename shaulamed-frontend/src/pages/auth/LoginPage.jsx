// src/pages/auth/LoginPage.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../../firebase/config';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await signInWithEmailAndPassword(auth, email, password);
      navigate('/'); // Redireciona para a Home após o login
    } catch (err) {
      setError('Email ou senha inválidos.');
    }
  };

  return (
    <div className="login">
      <form onSubmit={handleLogin} className="login__form">
        <h1 className="login__title">ShaulaMed</h1>
        {error && <p style={{color: 'red', textAlign: 'center'}}>{error}</p>}
        {/* ... resto do formulário HTML convertido para JSX ... */}
        <div className="login__content">
          {/* Email */}
          <div className="login__box">
            <i className="ri-user-3-line login__icon"></i>
            <div className="login__box-input">
              <input type="email" required className="login__input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder=" " />
              <label className="login__label">Email</label>
            </div>
          </div>
          {/* Senha */}
          <div className="login__box">
            <i className="ri-lock-2-line login__icon"></i>
            <div className="login__box-input">
              <input type="password" required className="login__input" value={password} onChange={(e) => setPassword(e.target.value)} placeholder=" " />
              <label className="login__label">Senha</label>
            </div>
          </div>
        </div>
        <button type="submit" className="login__button">Entrar</button>
        <p className="login__register">
          Não tem uma conta? <Link to="/cadastro">Registe-se</Link>
        </p>
      </form>
    </div>
  );
};
export default LoginPage;