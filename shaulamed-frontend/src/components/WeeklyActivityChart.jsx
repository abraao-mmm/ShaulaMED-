// src/components/WeeklyActivityChart.jsx

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import './WeeklyActivityChart.css';

// Componente customizado para o Tooltip, para combinar com o design
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="label">{`${label} : ${payload[0].value}`}</p>
      </div>
    );
  }
  return null;
};

const WeeklyActivityChart = ({ stats }) => {
  if (!stats) return null;

  // O backend nos dá o total e a porcentagem, então calculamos o resto
  const total = stats['Total de Casos Analisados'] || 0;
  const agreementPercentage = stats['% de Concordância com IA'] || 0;
  const agreementCount = Math.round((total * agreementPercentage) / 100);
  const divergenceCount = total - agreementCount;

  const chartData = [
    { name: 'Total', value: total, color: '#a855f7' },
    { name: 'Concordância', value: agreementCount, color: '#4ade80' },
    { name: 'Divergência', value: divergenceCount, color: '#f87171' },
  ];

  return (
    <div className="chart-widget">
      <h3>Atividade da Semana</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
            <XAxis dataKey="name" stroke="rgba(255, 255, 255, 0.7)" />
            <YAxis stroke="rgba(255, 255, 255, 0.7)" />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(147, 112, 219, 0.1)' }} />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default WeeklyActivityChart;