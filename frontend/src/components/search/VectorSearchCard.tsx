'use client';

import { useState } from 'react';
import Link from 'next/link';
import axios from 'axios';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface SearchResult {
  id: string;
  score: number;
  oasis_code: string;
  label: string;
  lead_statement?: string;
  main_duties?: string;
}

export default function VectorSearchCard() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/vector/search`, {
        query: query
      });
      
      const data = response.data as { results: SearchResult[] };
      // Show only top 3 results for the compact card
      setResults(data.results.slice(0, 3));
    } catch (err) {
      console.error('Search error:', err);
      setError('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-medium text-gray-700">Career Search</h3>
        <Link
          href="/vector-search"
          className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
        >
          <span>Advanced search</span>
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
            <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"></path>
          </svg>
        </Link>
      </div>

      <form onSubmit={handleSearch} className="mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search careers..."
            className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <LoadingSpinner size="sm" color="white" />
            ) : (
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
              </svg>
            )}
          </button>
        </div>
        {error && <p className="text-red-600 text-xs mt-1">{error}</p>}
      </form>

      <div className="space-y-3">
        {results.length > 0 ? (
          results.map((result) => (
            <div
              key={result.id}
              className="p-3 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
            >
              <div className="flex justify-between items-start">
                <h4 className="font-medium text-sm text-gray-900 line-clamp-1">
                  {result.label}
                </h4>
                <span className="text-xs text-blue-600 font-medium ml-2">
                  {Math.round(result.score * 100)}% match
                </span>
              </div>
              {result.lead_statement && (
                <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                  {result.lead_statement}
                </p>
              )}
            </div>
          ))
        ) : (
          !loading && query && (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500">No results found</p>
            </div>
          )
        )}
        {!query && !loading && (
          <div className="text-center py-4">
            <p className="text-sm text-gray-500">Enter a search query to find careers</p>
          </div>
        )}
      </div>
    </div>
  );
}