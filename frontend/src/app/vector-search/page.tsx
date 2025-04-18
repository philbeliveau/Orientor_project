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
  all_fields?: { [key: string]: string };
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
      setSavingIds(prev => new Set(prev).add(result.id));
      setSaveSuccess(null);

      const recommendation = {
        oasis_code: result.oasis_code,
        label: result.label,
        description: result.lead_statement || '',
        main_duties: result.main_duties || '',
        role_creativity: undefined,
        role_leadership: undefined,
        role_digital_literacy: undefined,
        role_critical_thinking: undefined,
        role_problem_solving: undefined,
        all_fields: result.all_fields || {}
      };

      await saveRecommendation(recommendation);

      setSaveSuccess(`Successfully saved "${result.label}" to your Space`);
      setSavingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(result.id);
        return newSet;
      });

      setTimeout(() => {
        setSaveSuccess(null);
      }, 3000);
    } catch (err: any) {
      if (err.response?.status === 400 && err.response?.data?.detail === "This recommendation is already saved.") {
        setError('This recommendation is already in your Space.');
      } else {
        setError('Failed to save to Space. Please try again.');
      }
      console.error('Save error:', err);
      setSavingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(result.id);
        return newSet;
      });
    }
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
                  <div key={result.id} className="card p-6 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-xl font-bold text-primary-teal">{result.label || 'No label available'}</h3>
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
                    <div className="space-y-3">
                      <p className="text-sm text-neutral-600">Job title: {result.label}</p>
                      {result.lead_statement && (
                        <div>
                          <h4 className="font-medium text-sm text-neutral-600 mb-1">Description</h4>
                          <p className="text-sm text-neutral-600">{result.lead_statement}</p>
                        </div>
                      )}
                      {result.main_duties && (
                        <div>
                          <h4 className="font-medium text-sm text-neutral-600 mb-1">Main Duties</h4>
                          <p className="text-sm text-neutral-600">{result.main_duties}</p>
                        </div>
                      )}
                      {result.all_fields && (
                        <div>
                          <h4 className="font-medium text-sm text-neutral-600 mb-1">Additional Info</h4>
                          <div className="text-sm text-neutral-600 grid grid-cols-2 gap-x-6 gap-y-1">
                            {Object.entries(result.all_fields).map(([key, value]) => (
                              <div key={key} className="flex gap-2">
                                <span className="font-semibold capitalize whitespace-nowrap">{key.replace(/_/g, ' ')}:</span>
                                <span className="text-neutral-600">{value}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      <p className="text-xs text-neutral-500 italic mt-2">
                        Save to your Space to view all job details and requirements
                      </p>
                    </div>
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