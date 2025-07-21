import React, { useState, useEffect } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ResponsiveContainer } from 'recharts';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { analyzeCareerFit } from '@/services/spaceService';
import type { Recommendation, SavedJob, CareerFitResponse } from '@/services/spaceService';

interface CareerFitAnalyzerProps {
  job: Recommendation | SavedJob;
  jobSource: 'esco' | 'oasis';
}


const CareerFitAnalyzer: React.FC<CareerFitAnalyzerProps> = ({ job, jobSource }) => {
  const [fitAnalysis, setFitAnalysis] = useState<CareerFitResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLLMChat, setShowLLMChat] = useState(true); // Show by default
  const [llmQuery, setLlmQuery] = useState('');
  const [llmResponse, setLlmResponse] = useState('');
  const [llmLoading, setLlmLoading] = useState(false);

  // Determine job ID based on type
  const jobId = jobSource === 'esco' ? 
    ('oasis_code' in job ? job.oasis_code : job.id?.toString() || '') :  // ESCO jobs use oasis_code
    ('esco_id' in job ? job.esco_id : job.id?.toString() || '');        // OaSIS jobs use esco_id

  useEffect(() => {
    fetchCareerFitAnalysis();
  }, [jobId, jobSource]);

  const fetchCareerFitAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      const analysis = await analyzeCareerFit(jobId, jobSource);
      setFitAnalysis(analysis);
    } catch (err: any) {
      setError('Failed to analyze career fit');
      console.error('Career fit analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLLMQuery = async () => {
    if (!llmQuery.trim()) return;

    setLlmLoading(true);
    try {
      // Get auth token
      const token = localStorage.getItem('access_token');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // This would call your LLM service with the job context and user query
      const response = await fetch(`${apiUrl}/api/v1/careers/llm-query`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify({
          job_id: jobId,
          job_source: jobSource,
          query: llmQuery,
          context: fitAnalysis
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setLlmResponse(data.response);
    } catch (err) {
      console.error('LLM query error:', err);
      setLlmResponse('Failed to get AI response. Please try again.');
    } finally {
      setLlmLoading(false);
    }
  };

  const prepareRadarData = () => {
    if (!fitAnalysis?.skill_match) return [];

    return Object.entries(fitAnalysis.skill_match).map(([skill, match]) => ({
      skill: match.skill_name,
      user: match.user_level || 0,
      required: match.required_level || 0,
      match: match.match_percentage
    }));
  };

  const getSeverity = (score: number): 'low' | 'medium' | 'high' => {
    if (score >= 80) return 'low';
    if (score >= 60) return 'medium';
    return 'high';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !fitAnalysis) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">⚠️ {error || 'Unable to analyze career fit'}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overall Fit Score */}
      <div className="text-center p-6 rounded-lg" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text)' }}>
          Career Fit Score
        </h2>
        <div className="relative inline-flex items-center justify-center">
          <svg className="w-32 h-32">
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="var(--border)"
              strokeWidth="12"
              fill="none"
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke={fitAnalysis.fit_score >= 80 ? '#10B981' : fitAnalysis.fit_score >= 60 ? '#F59E0B' : '#EF4444'}
              strokeWidth="12"
              fill="none"
              strokeDasharray={`${(fitAnalysis.fit_score / 100) * 352} 352`}
              strokeLinecap="round"
              transform="rotate(-90 64 64)"
            />
          </svg>
          <div className="absolute">
            <span className="text-3xl font-bold" style={{ color: 'var(--text)' }}>
              {Math.round(fitAnalysis.fit_score)}%
            </span>
          </div>
        </div>
        <p className="mt-4 text-sm" style={{ color: 'var(--text-secondary)' }}>
          {fitAnalysis.recommendations[0]}
        </p>
      </div>

      {/* GraphSAGE Skills for OaSIS jobs */}
      {jobSource === 'oasis' && (
        <div className="p-6 rounded-lg" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text)' }}>
            Top 5 High-Relevance Skills (GraphSAGE Analysis)
          </h3>
          <div className="space-y-3">
            {('graphsage_skills' in job && job.graphsage_skills && job.graphsage_skills.length > 0) ? (
              job.graphsage_skills.map((skill, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-blue-50">
                  <div className="flex-1">
                    <p className="font-medium text-blue-900">{skill.skill_name}</p>
                    <p className="text-sm text-blue-700">{skill.description}</p>
                  </div>
                  <div className="ml-4 text-right">
                    <p className="text-lg font-bold text-blue-900">
                      {(skill.relevance_score * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-blue-700">relevance</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Loading GraphSAGE skill analysis...
              </p>
            )}
          </div>
        </div>
      )}

      {/* Skill Comparison Radar - Only for ESCO jobs */}
      {jobSource === 'esco' && (
        <div className="p-6 rounded-lg" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text)' }}>
            Skill Match Analysis
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={prepareRadarData()}>
              <PolarGrid stroke="var(--border)" />
              <PolarAngleAxis dataKey="skill" style={{ fill: 'var(--text-secondary)' }} />
              <PolarRadiusAxis angle={30} domain={[0, 5]} style={{ fill: 'var(--text-secondary)' }} />
              <Radar name="Your Skills" dataKey="user" stroke="#10B981" fill="#10B981" fillOpacity={0.6} />
              <Radar name="Required Skills" dataKey="required" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.6} />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Gap Analysis - Only for ESCO jobs */}
      {jobSource === 'esco' && fitAnalysis.gap_analysis.skill_gaps.length > 0 && (
        <div className="p-6 rounded-lg" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text)' }}>
            Skills to Develop
          </h3>
          <div className="space-y-3">
            {fitAnalysis.gap_analysis.skill_gaps.map((gap, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-yellow-50">
                <div>
                  <p className="font-medium text-yellow-900">{gap.skill}</p>
                  <p className="text-sm text-yellow-700">
                    Current: {gap.current}/5 → Required: {gap.required}/5
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-yellow-900">Gap: {gap.gap.toFixed(1)}</p>
                  <p className="text-xs text-yellow-700">points needed</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* LLM Chat Interface */}
      <div className="p-6 rounded-lg" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold" style={{ color: 'var(--text)' }}>
            AI Career Advisor
          </h3>
          <button
            onClick={() => setShowLLMChat(!showLLMChat)}
            className="text-sm px-3 py-1 rounded-full bg-blue-100 text-blue-700 hover:bg-blue-200"
          >
            {showLLMChat ? 'Hide' : 'Show'} Chat
          </button>
        </div>

        {showLLMChat && (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>
                Ask questions about this career path:
              </p>
              <div className="flex flex-wrap gap-2 mb-4">
                <button
                  onClick={() => setLlmQuery("Why would I want to do this job?")}
                  className="text-xs px-3 py-1 bg-white border rounded-full hover:bg-gray-50"
                >
                  Why this job?
                </button>
                <button
                  onClick={() => setLlmQuery("What are the 3 biggest barriers?")}
                  className="text-xs px-3 py-1 bg-white border rounded-full hover:bg-gray-50"
                >
                  Top barriers?
                </button>
                <button
                  onClick={() => setLlmQuery("How long to qualify?")}
                  className="text-xs px-3 py-1 bg-white border rounded-full hover:bg-gray-50"
                >
                  Time to qualify?
                </button>
                <button
                  onClick={() => setLlmQuery("Do I need a PhD?")}
                  className="text-xs px-3 py-1 bg-white border rounded-full hover:bg-gray-50"
                >
                  PhD required?
                </button>
              </div>
              
              <div className="flex gap-2">
                <input
                  type="text"
                  value={llmQuery}
                  onChange={(e) => setLlmQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleLLMQuery()}
                  placeholder="Ask about qualifications, timeline, barriers..."
                  className="flex-1 px-3 py-2 border rounded-lg text-sm"
                  style={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)' }}
                />
                <button
                  onClick={handleLLMQuery}
                  disabled={llmLoading || !llmQuery.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {llmLoading ? '...' : 'Ask'}
                </button>
              </div>
            </div>

            {llmResponse && (
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-blue-900 whitespace-pre-wrap">{llmResponse}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Career Path Recommendations */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold" style={{ color: 'var(--text)' }}>
          Recommended Actions
        </h3>
        {fitAnalysis.recommendations.slice(1).map((rec, index) => (
          <div key={index} className="flex items-start gap-3 p-4 rounded-lg" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
            <span className="text-xl">💡</span>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{rec}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CareerFitAnalyzer;