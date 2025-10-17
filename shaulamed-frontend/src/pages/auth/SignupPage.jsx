// src/pages/auth/SignupPage.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../../firebase/config';

const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

const SignupPage = () => {
    const [formData, setFormData] = useState({
        nome: '', email: '', crm: '', especialidade: '', password: ''
    });
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    const handleSignUp = async (e) => {
        e.preventDefault();
        setError('');
        try {
            // ... (lógica de cadastro que você já tem)
            const userCredential = await createUserWithEmailAndPassword(auth, formData.email, formData.password);
            const user = userCredential.user;

            const response = await fetch(`${API_BASE_URL}/medico/criar_perfil`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    uid: user.uid,
                    email: formData.email,
                    nome_completo: formData.nome,
                    apelido: formData.nome.split(' ')[0],
                    crm: formData.crm,
                    especialidade: formData.especialidade,
                    sexo: ""
                })
            });
            if (!response.ok) throw new Error('Falha ao criar perfil no backend.');

            await auth.signOut();
            alert("Conta criada com sucesso! Por favor, faça o login.");
            navigate('/login');
        } catch (err) {
            setError(err.message || 'Ocorreu um erro ao criar a conta.');
        }
    };

  return (
    <div className="login">
      <form onSubmit={handleSignUp} className="login__form">
        <h1 className="login__title">Criar Conta</h1>
        {error && <p className="form-error-message">{error}</p>}

        <div className="login__content">
          <div className="login__box">
            <i className="ri-user-smile-line login__icon"></i>
            <div className="login__box-input">
              <input type="text" name="nome" required className="login__input" id="signup-nome-input" placeholder=" " onChange={handleChange}/>
              <label htmlFor="signup-nome-input" className="login__label">Nome Completo</label>
            </div>
          </div>
          <div className="login__box">
            <i className="ri-mail-line login__icon"></i>
            <div className="login__box-input">
              <input type="email" name="email" required className="login__input" id="signup-email-input" placeholder=" " onChange={handleChange}/>
              <label htmlFor="signup-email-input" className="login__label">Email</label>
            </div>
          </div>
          <div className="login__box">
            <i className="ri-file-user-line login__icon"></i>
            <div className="login__box-input">
              <input type="text" name="crm" required className="login__input" id="signup-crm-input" placeholder=" " onChange={handleChange}/>
              <label htmlFor="signup-crm-input" className="login__label">CRM (ex: 12345-AM)</label>
            </div>
          </div>
          <div className="login__box">
            <i className="ri-briefcase-4-line login__icon"></i>
            <div className="login__box-input">
              <input type="text" name="especialidade" required className="login__input" id="signup-especialidade-input" placeholder=" " onChange={handleChange}/>
              <label htmlFor="signup-especialidade-input" className="login__label">Especialidade</label>
            </div>
          </div>
          <div className="login__box">
            <i className="ri-lock-2-line login__icon"></i>
            <div className="login__box-input">
              <input type={showPassword ? "text" : "password"} name="password" required className="login__input" id="signup-password-input" placeholder=" " onChange={handleChange}/>
              <label htmlFor="signup-password-input" className="login__label">Senha</label>
              <i className={showPassword ? 'ri-eye-line login__eye' : 'ri-eye-off-line login__eye'} onClick={() => setShowPassword(!showPassword)}></i>
            </div>
          </div>
        </div>

        <button type="submit" className="login__button">Criar Conta</button>
        <p className="login__register">
          Já tem uma conta? <Link to="/login">Voltar ao Login</Link>
        </p>
      </form>
    </div>
  );
};
export default SignupPage;