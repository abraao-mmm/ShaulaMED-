// src/pages/auth/SignupPage.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../../firebase/config';

const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

const SignupPage = () => {
    const [formData, setFormData] = useState({ nome: '', email: '', crm: '', especialidade: '', password: '' });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    const handleSignUp = async (e) => {
        e.preventDefault();
        setError('');
        try {
            // Passo 1: Criar usuário no Auth
            const userCredential = await createUserWithEmailAndPassword(auth, formData.email, formData.password);
            const user = userCredential.user;

            // Passo 2: Criar perfil no backend
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

            // Logout para forçar o login
            await auth.signOut();
            alert("Conta criada com sucesso! Por favor, faça o login.");
            navigate('/login');
        } catch (err) {
            setError(err.message);
        }
    };

  return (
    <div className="login">
      <form onSubmit={handleSignUp} className="login__form">
        <h1 className="login__title">Criar Conta</h1>
        {error && <p style={{color: 'red', textAlign: 'center'}}>{error}</p>}
        {/* ... Formulário de Cadastro em JSX ... */}
        <div className="login__content">
          {/* Nome, Email, CRM, etc. */}
           <input name="nome" placeholder="Nome Completo" onChange={handleChange} required className="login__input"/>
           <input name="email" type="email" placeholder="Email" onChange={handleChange} required className="login__input"/>
           <input name="crm" placeholder="CRM" onChange={handleChange} required className="login__input"/>
           <input name="especialidade" placeholder="Especialidade" onChange={handleChange} required className="login__input"/>
           <input name="password" type="password" placeholder="Senha" onChange={handleChange} required className="login__input"/>
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