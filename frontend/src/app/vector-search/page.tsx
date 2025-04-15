'use client';

import { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';

interface SearchResult {
  id: string;
  score: number;
  oasis_code: string;
  label: string;
  lead_statement?: string;
  main_duties?: string;
}

export default function VectorSearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }
    
    setLoading(true);
    setError('');
    
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

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">OaSIS Vector Search</h1>
        
        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your search query..."
              className="flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:text-gray-900"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
          {error && <p className="text-red-500 mt-2">{error}</p>}
        </form>
        
        <div>
          {results.length > 0 ? (
            <div>
              <h2 className="text-xl font-semibold mb-4">Search Results</h2>
              <div className="space-y-6">
                {results.map((result) => (
                  <div key={result.id} className="border p-4 rounded shadow-sm">
                    <div className="flex justify-between items-start">
                      <h3 className="text-lg font-medium">{result.label}</h3>
                      <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        Score: {(result.score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mb-2">OaSIS Code: {result.oasis_code}</p>
                    
                    {result.lead_statement && (
                      <div className="mt-2">
                        <h4 className="font-medium text-sm">Description:</h4>
                        <p className="text-sm">{result.lead_statement}</p>
                      </div>
                    )}
                    
                    {result.main_duties && (
                      <div className="mt-2">
                        <h4 className="font-medium text-sm">Main Duties:</h4>
                        <p className="text-sm">{result.main_duties}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            !loading && (
              <p className="text-center text-gray-500">
                No results to display. Try searching for occupations or skills.
              </p>
            )
          )}
        </div>
      </div>
    </MainLayout>
  );
} 