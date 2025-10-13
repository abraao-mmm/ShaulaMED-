// src/components/CoachInsightWidget.jsx

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './CoachInsightWidget.css';

const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";
const USER_ID = "TEST_UID_THALLES"; // UID de teste

const CoachInsightWidget = ({ insightText, divergenceCase }) => {
  const [reflexao, setReflexao] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reflexao.trim()) return;

    setIsSubmitting(true);
    setError('');

    try {
      // O ID da consulta vem do objeto `divergenceCase`
      const consultaId = divergenceCase?.id;
      if (!consultaId) {
        throw new Error("ID da consulta para reflexão não encontrado.");
      }

      // O payload esperado pelo backend
      const payload = {
        texto_resposta: reflexao,
      };

      const response = await fetch(`${API_BASE_URL}/consulta/${consultaId}/salvar_reflexao_medico?uid=${USER_ID}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Falha ao salvar a reflexão.');
      }

      setIsSubmitted(true);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!insightText) {
      return null; // Não renderiza nada se não houver texto do coach
  }

  return (
    <motion.div 
        className="coach-widget"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
    >
      <div className="chat chat-left">
        <div className="chat-avatar">
          <div className="initials">S</div>
        </div>
        <div className="chat-body">
          <div className="chat-bubble">
            <div className="chat-content">
              <p>{insightText}</p>
            </div>
          </div>
        </div>
      </div>

      {divergenceCase && !isSubmitted && (
        <form className="chat-form" onSubmit={handleSubmit}>
          <textarea
            value={reflexao}
            onChange={(e) => setReflexao(e.target.value)}
            placeholder="Digite sua reflexão aqui..."
            disabled={isSubmitting}
          />
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Salvando...' : 'Salvar Reflexão'}
          </button>
        </form>
      )}

      {isSubmitted && (
        <p className="success-message">Obrigado! Sua reflexão foi salva e ajudará a calibrar a IA.</p>
      )}
      {error && <p className="error-message">{error}</p>}
    </motion.div>
  );
};

export default CoachInsightWidget;