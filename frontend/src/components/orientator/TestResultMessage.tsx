import React, { useState } from 'react';
import { Brain, BarChart3, TrendingUp, Award, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { SaveActionButton } from '../chat/SaveActionButton';
import { ComponentAction } from '../chat/MessageComponent';

interface TestDimension {
  name: string;
  score: number;
  percentile?: number;
  description?: string;
  interpretation?: string;
}

interface TestResultData {
  test_type: 'hexaco' | 'holland' | 'other';
  test_name: string;
  dimensions: TestDimension[];
  overall_profile?: string;
  career_implications?: string[];
  strengths?: string[];
  development_areas?: string[];
  completion_date?: string;
  validity_score?: number;
}

interface TestResultMessageProps {
  data: TestResultData;
  actions: ComponentAction[];
  onAction: (action: ComponentAction) => void;
  saved?: boolean;
  className?: string;
}

const hexacoColors = {
  'Honesty-Humility': 'bg-purple-500',
  'Emotionality': 'bg-red-500',
  'Extraversion': 'bg-yellow-500',
  'Agreeableness': 'bg-green-500',
  'Conscientiousness': 'bg-blue-500',
  'Openness': 'bg-indigo-500'
};

const hollandColors = {
  'Realistic': 'bg-orange-500',
  'Investigative': 'bg-cyan-500',
  'Artistic': 'bg-pink-500',
  'Social': 'bg-green-500',
  'Enterprising': 'bg-red-500',
  'Conventional': 'bg-gray-500'
};

export const TestResultMessage: React.FC<TestResultMessageProps> = ({
  data,
  actions,
  onAction,
  saved,
  className = ""
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [expandedDimension, setExpandedDimension] = useState<string | null>(null);

  const handleSave = async () => {
    const saveAction = actions.find(a => a.type === 'save');
    if (saveAction) {
      onAction(saveAction);
    }
  };

  const getColorForDimension = (dimension: string): string => {
    if (data.test_type === 'hexaco') {
      return hexacoColors[dimension as keyof typeof hexacoColors] || 'bg-gray-500';
    } else if (data.test_type === 'holland') {
      return hollandColors[dimension as keyof typeof hollandColors] || 'bg-gray-500';
    }
    return 'bg-blue-500';
  };

  const maxScore = Math.max(...data.dimensions.map(d => d.score));

  return (
    <div className={`border border-gray-200 rounded-lg p-4 bg-white ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <Brain className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
            <h3 className="font-medium text-gray-900">{data.test_name} Results</h3>
            {data.completion_date && (
              <p className="text-sm text-gray-600">Completed on {(() => {
                const date = new Date(data.completion_date);
                return isNaN(date.getTime()) ? 'Date invalide' : date.toLocaleDateString();
              })()}</p>
            )}
          </div>
        </div>
        <SaveActionButton onSave={handleSave} saved={saved} size="sm" variant="outline" />
      </div>

      {/* Validity Score */}
      {data.validity_score && (
        <div className="mb-4 p-2 bg-green-50 rounded-lg flex items-center gap-2">
          <Award className="w-4 h-4 text-green-600" />
          <span className="text-sm text-green-700">
            Test validity: {data.validity_score}% - Results are reliable
          </span>
        </div>
      )}

      {/* Overall Profile */}
      {data.overall_profile && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-900">{data.overall_profile}</p>
        </div>
      )}

      {/* Dimensions Chart */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Your Profile</h4>
        <div className="space-y-3">
          {data.dimensions.map((dimension) => (
            <div key={dimension.name}>
              <button
                onClick={() => setExpandedDimension(
                  expandedDimension === dimension.name ? null : dimension.name
                )}
                className="w-full text-left"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">{dimension.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-gray-900">{dimension.score}</span>
                    {dimension.percentile && (
                      <span className="text-xs text-gray-500">({dimension.percentile}th percentile)</span>
                    )}
                    {dimension.description && (
                      expandedDimension === dimension.name ? 
                        <ChevronUp className="w-4 h-4 text-gray-400" /> : 
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                </div>
              </button>
              
              {/* Score Bar */}
              <div className="relative w-full bg-gray-200 rounded-full h-6">
                <div 
                  className={`h-6 rounded-full transition-all duration-500 ${getColorForDimension(dimension.name)}`}
                  style={{ width: `${(dimension.score / maxScore) * 100}%` }}
                />
                <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white mix-blend-difference">
                  {dimension.score}
                </span>
              </div>

              {/* Expanded Description */}
              {expandedDimension === dimension.name && dimension.description && (
                <div className="mt-2 p-2 bg-gray-50 rounded text-sm text-gray-700">
                  <p>{dimension.description}</p>
                  {dimension.interpretation && (
                    <p className="mt-1 font-medium">{dimension.interpretation}</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Show/Hide Details Button */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="w-full py-2 text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center justify-center gap-1"
      >
        {showDetails ? 'Hide' : 'Show'} Detailed Analysis
        {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {/* Detailed Analysis */}
      {showDetails && (
        <div className="mt-4 space-y-4 border-t border-gray-200 pt-4">
          {/* Career Implications */}
          {data.career_implications && data.career_implications.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                <TrendingUp className="w-4 h-4" />
                Career Implications
              </h4>
              <ul className="space-y-1">
                {data.career_implications.map((implication, idx) => (
                  <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-blue-500 mt-0.5">•</span>
                    <span>{implication}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Strengths */}
          {data.strengths && data.strengths.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Key Strengths</h4>
              <div className="flex flex-wrap gap-2">
                {data.strengths.map((strength, idx) => (
                  <span key={idx} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                    {strength}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Development Areas */}
          {data.development_areas && data.development_areas.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Areas for Development</h4>
              <div className="flex flex-wrap gap-2">
                {data.development_areas.map((area, idx) => (
                  <span key={idx} className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm">
                    {area}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="mt-4 pt-3 border-t border-gray-200 flex items-center gap-2">
        {actions.filter(a => a.type !== 'save').map((action, index) => (
          <button
            key={index}
            onClick={() => onAction(action)}
            className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            {action.label}
          </button>
        ))}
      </div>

      {/* Info */}
      <div className="mt-3 flex items-start gap-1 text-xs text-gray-500">
        <Info className="w-3 h-3 mt-0.5 flex-shrink-0" />
        <span>Your results are confidential and used only to provide personalized career guidance.</span>
      </div>
    </div>
  );
};