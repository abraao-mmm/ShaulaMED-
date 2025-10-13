// src/pages/ReportsPage.jsx

import React, { useState, useEffect } from 'react';
import LightRays from '../components/LightRays';
import SpotlightCard from '../components/SpotlightCard';
import './ReportsPage.css';

const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";
const USER_ID = "TEST_UID_THALLES"; // UID de teste

const ReportsPage = () => {
  const [reportData, setReportData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReportData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/medico/${USER_ID}/relatorio_semanal`);
        if (!response.ok) {
          throw new Error('Falha ao buscar os dados do relatório.');
        }
        const data = await response.json();
        setReportData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchReportData();
  }, []);

  if (isLoading) {
    return <div className="loading-state">Carregando Relatórios...</div>;
  }

  if (error) {
    return <div className="error-state">Erro: {error}</div>;
  }

  // Os dados dos cards vêm do backend
  const kpiData = reportData?.dados_estruturados?.stats_semanais || {};

  return (
    <div className="reports-page">
      <LightRays />
      <div className="reports-content">
        <header className="reports-header">
          <h1>Seu Painel Semanal</h1>
          <p>Uma análise da sua prática clínica recente.</p>
        </header>

        <div className="kpi-cards-container">
          <SpotlightCard 
            title="Total de Casos Analisados" 
            value={kpiData['Total de Casos Analisados'] ?? '0'} 
          />
          <SpotlightCard 
            title="% de Concordância com IA" 
            value={`${kpiData['% de Concordância com IA'] ?? '0'}%`}
          />
          <SpotlightCard 
            title="Novos Diagnósticos Investigados" 
            value={kpiData['Novos Diagnósticos Investigados'] ?? '0'}
          />
        </div>

        {/* Placeholder para os próximos componentes */}
        <div className="placeholder-section">
          <p>Em breve: Insight do Coach Clínico e Histórico Detalhado.</p>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;