import React from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';
import type { SkillsComparison } from '@/services/spaceService';

// Register required Chart.js components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface SkillRadarChartProps {
  skillComparison: SkillsComparison;
}

const SkillRadarChart: React.FC<SkillRadarChartProps> = ({ skillComparison }) => {
  const data = {
    labels: ['Creativity', 'Leadership', 'Digital Literacy', 'Critical Thinking', 'Problem Solving'],
    datasets: [
      {
        label: 'Your Skills',
        data: [
          skillComparison.creativity.user_skill || 0,
          skillComparison.leadership.user_skill || 0,
          skillComparison.digital_literacy.user_skill || 0,
          skillComparison.critical_thinking.user_skill || 0,
          skillComparison.problem_solving.user_skill || 0
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.4)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
      },
      {
        label: 'Required Skills',
        data: [
          skillComparison.creativity.role_skill || 0,
          skillComparison.leadership.role_skill || 0,
          skillComparison.digital_literacy.role_skill || 0,
          skillComparison.critical_thinking.role_skill || 0,
          skillComparison.problem_solving.role_skill || 0
        ],
        backgroundColor: 'rgba(255, 99, 132, 0.4)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(255, 99, 132, 1)',
      }
    ]
  };

  const options = {
    scales: {
      r: {
        beginAtZero: true,
        max: 5,
        ticks: {
          stepSize: 1
        }
      }
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ${context.raw}`;
          }
        }
      }
    }
  };

  return (
    <div className="h-96 p-4">
      <Radar data={data} options={options} />
    </div>
  );
};

export default SkillRadarChart; 