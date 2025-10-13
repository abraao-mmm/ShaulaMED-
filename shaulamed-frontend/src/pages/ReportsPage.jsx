// src/pages/ReportsPage.jsx

import React, { useState, useEffect } from 'react';
import LightRays from '../components/LightRays';
import SpotlightCard from '../components/SpotlightCard';
import CoachInsightWidget from '../components/CoachInsightWidget';
import WeeklyActivityChart from '../components/WeeklyActivityChart';
import './ReportsPage.css';

const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";
const USER_ID = "TEST_UID_THALLES"; // UID de teste para desenvolvimento

const ReportsPage = () => {
  const [reportData, setReportData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReportData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/medico/${USER_ID}/relatorio_semanal`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Falha ao buscar os dados do relatório.');
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
    return <div className="loading-state">Carregando Painel Reflexivo...</div>;
  }

  if (error) {
    return <div className="error-state">Erro ao carregar o painel: {error}</div>;
  }

  // Dados para os componentes, extraídos da resposta da API
  const kpiData = reportData?.dados_estruturados?.stats_semanais || {};
  const coachText = reportData?.texto_coach;
  const divergenceData = reportData?.dados_estruturados?.exemplo_divergencia;

  return (
    <div className="reports-page">
      <LightRays />
      <div className="reports-content">
        <header className="reports-header">
          <h1>Seu Painel Semanal</h1>
          <p>Uma análise da sua prática clínica recente para impulsionar a reflexão.</p>
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

        <div className="analysis-grid">
            <CoachInsightWidget 
              insightText={coachText}
              divergenceCase={divergenceData}
            />
            <WeeklyActivityChart 
              stats={kpiData}
            />
        </div>

      </div>
    </div>
  );
};

export default ReportsPage;