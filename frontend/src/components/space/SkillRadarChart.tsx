import React from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';
import { Radar } from 'react-chartjs-2';
import type { SkillComparison, UserSkills } from '@/services/spaceService';

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
  skillComparison: SkillComparison;
}

const SkillRadarChart: React.FC<SkillRadarChartProps> = ({ skillComparison }) => {
  // Format the skills label for display (capitalize and replace underscores with spaces)
  const formatSkillLabel = (skill: string): string => {
    return skill
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const skillKeys = ['creativity', 'leadership', 'digital_literacy', 'critical_thinking', 'problem_solving'] as const;
  type SkillKey = typeof skillKeys[number];
  
  // Extract keys and format them
  const skills = skillKeys.map(formatSkillLabel);
  
  // Extract user and role skill values, replacing undefined with 0
  const userSkills = skillKeys.map(key => skillComparison.user_skills[key as keyof UserSkills] || 0);
  const roleSkills = skillKeys.map(key => skillComparison.job_skills[key as keyof UserSkills] || 0);

  const chartData = {
    labels: skills,
    datasets: [
      {
        label: 'Your Skills',
        data: userSkills,
        backgroundColor: 'rgba(125, 91, 166, 0.2)',
        borderColor: 'rgba(125, 91, 166, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(125, 91, 166, 1)',
        pointHoverBackgroundColor: 'rgba(125, 91, 166, 1)',
        pointHoverBorderColor: '#fff',
      },
      {
        label: 'Role Requirements',
        data: roleSkills,
        backgroundColor: 'rgba(89, 194, 201, 0.2)',
        borderColor: 'rgba(89, 194, 201, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(89, 194, 201, 1)',
        pointHoverBackgroundColor: 'rgba(89, 194, 201, 1)',
        pointHoverBorderColor: '#fff',
      },
    ],
  };

  const chartOptions = {
    scales: {
      r: {
        angleLines: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        pointLabels: {
          color: 'rgba(255, 255, 255, 0.7)',
          font: {
            size: 12,
          },
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.7)',
          backdropColor: 'transparent',
          stepSize: 1,
          max: 5,
          min: 0,
        },
      },
    },
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: 'rgba(255, 255, 255, 0.7)',
          font: {
            size: 12,
          },
          boxWidth: 12,
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(26, 32, 44, 0.8)',
        titleColor: 'rgba(255, 255, 255, 0.9)',
        bodyColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
      },
    },
    maintainAspectRatio: false,
    elements: {
      line: {
        tension: 0.2,
      },
    },
  };

  return (
    <div className="w-full h-full">
      <Radar data={chartData} options={chartOptions} />
    </div>
  );
};

export default SkillRadarChart; 