'use client';

import { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { saveRecommendation } from '@/services/spaceService';

interface SearchResult {
  id: string;
  score: number;
  oasis_code: string;
  label: string;
  lead_statement?: string;
  main_duties?: string;
}

interface SkillValues {
  role_creativity?: number | null;
  role_leadership?: number | null;
  role_digital_literacy?: number | null;
  role_critical_thinking?: number | null;
  role_problem_solving?: number | null;
}

export default function VectorSearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingIds, setSavingIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState('');
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }
    
    setLoading(true);
    setError('');
    setSaveSuccess(null);
    
    try {
      const response = await fetch('http://localhost:8000/vector/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 5 })
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      setResults(data.results);
    } catch (err) {
      setError('Failed to search. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveToSpace(result: SearchResult) {
    try {
      // Mark this result as saving
      setSavingIds(prev => new Set(prev).add(result.id));
      setSaveSuccess(null);
      
      // Extract skill levels from text if available
      const skills = extractSkillsFromText(result.lead_statement || '', result.main_duties || '');
      
      // Create recommendation object
      const recommendation = {
        oasis_code: result.oasis_code,
        label: result.label,
        description: result.lead_statement || '',
        main_duties: result.main_duties || '',
        saved_at: new Date().toISOString(),
        id: Date.now(), // Temporary ID that will be replaced by the backend
        ...skills
      };
      
      // Save to space
      await saveRecommendation(recommendation);
      
      // Show success message
      setSaveSuccess(`Successfully saved "${result.label}" to your Space`);
      
      // Remove from saving state
      setSavingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(result.id);
        return newSet;
      });
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSaveSuccess(null);
      }, 3000);
    } catch (err) {
      setError('Failed to save to Space. Please try again.');
      console.error('Save error:', err);
      
      // Remove from saving state
      setSavingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(result.id);
        return newSet;
      });
    }
  }

  // Helper function to extract skill levels from text
  function extractSkillsFromText(description: string, duties: string) {
    const text = `${description} ${duties}`;
    const skills = {
      role_creativity: 0,
      role_leadership: 0,
      role_digital_literacy: 0,
      role_critical_thinking: 0,
      role_problem_solving: 0
    };
    
    // Extract skills using regex
    const extractSkill = (skillName: string): number => {
      const regex = new RegExp(`${skillName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: (\\d+)`, 'i');
      const match = text.match(regex);
      return match ? parseFloat(match[1]) : 0;
    };
    
    skills.role_creativity = extractSkill('creativity');
    skills.role_leadership = extractSkill('leadership');
    skills.role_digital_literacy = extractSkill('digital_literacy');
    skills.role_critical_thinking = extractSkill('critical_thinking');
    skills.role_problem_solving = extractSkill('problem_solving');
    
    return skills;
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6 gradient-text">Career Recommendations</h1>
        
        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter skills, interests, or desired career..."
              className="input flex-1"
            />
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
          {error && <p className="text-red-400 mt-2">{error}</p>}
          {saveSuccess && (
            <div className="mt-2 p-2 bg-green-500/20 text-green-300 rounded-lg text-sm">
              {saveSuccess}
            </div>
          )}
        </form>
        
        <div>
          {results.length > 0 ? (
            <div>
              <h2 className="text-xl font-semibold mb-4">Search Results</h2>
              <div className="space-y-6">
                {results.map((result) => (
                  <div key={result.id} className="card">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-lg font-medium">{result.label}</h3>
                      <div className="flex items-center gap-2">
                        <span className="text-sm bg-primary-purple/30 text-primary-teal px-2 py-1 rounded-full">
                          Match: {(result.score * 100).toFixed(0)}%
                        </span>
                        <button
                          onClick={() => handleSaveToSpace(result)}
                          disabled={savingIds.has(result.id)}
                          className="btn btn-sm btn-secondary"
                        >
                          {savingIds.has(result.id) ? 'Saving...' : 'Save to Space'}
                        </button>
                      </div>
                    </div>
                    <p className="text-sm text-neutral-900 mb-3">OaSIS Code: {result.oasis_code}</p>
                    
                    {result.lead_statement && (
                      <div className="mb-3">
                        <h4 className="font-medium text-sm text-neutral-900">Description:</h4>
                        <p className="text-sm text-neutral-900">{result.lead_statement}</p>
                      </div>
                    )}
                    
                    {result.main_duties && (
                      <div className="mb-3">
                        <h4 className="font-medium text-sm text-neutral-900">Main Duties:</h4>
                        <p className="text-sm text-neutral-900">{result.main_duties}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            !loading && (
              <div className="text-center text-neutral-600 py-12">
                <p>No results to display. Try searching for occupations or skills.</p>
                <p className="mt-2 text-sm">Example searches: "software developer", "healthcare", "creative jobs"</p>
              </div>
            )
          )}
        </div>
      </div>
    </MainLayout>
  );
} 