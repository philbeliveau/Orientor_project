'use client';

/**
 * School Programs Search Component
 * 
 * Main search interface for school programs with filtering and results display
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Search, Filter, BookmarkPlus, ExternalLink, MapPin, Clock, DollarSign, GraduationCap } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

import SearchFilters from './SearchFilters';
import ProgramCard from './ProgramCard';
import ProgramDetails from './ProgramDetails';
import { useSchoolProgramsAPI } from './hooks/useSchoolProgramsAPI';
import { Program, SearchFilters as ISearchFilters, SearchResults } from './types';

const SchoolProgramsSearch: React.FC = () => {
  const [searchText, setSearchText] = useState('');
  const [filters, setFilters] = useState<ISearchFilters>({
    text: '',
    program_types: [],
    levels: [],
    location: {},
    languages: [],
    duration: {},
    budget: { currency: 'CAD' },
  });
  const [searchResults, setSearchResults] = useState<SearchResults | null>(null);
  const [selectedProgram, setSelectedProgram] = useState<Program | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  const api = useSchoolProgramsAPI();

  // Perform search
  const performSearch = useCallback(async (page: number = 1) => {
    setIsLoading(true);
    try {
      const searchFilters = { ...filters, text: searchText };
      const results = await api.searchPrograms(searchFilters, page);
      setSearchResults(results);
      setCurrentPage(page);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, [api, filters, searchText]);

  // Initial search on component mount
  useEffect(() => {
    performSearch();
  }, []);

  // Handle search submission
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    performSearch(1);
  };

  // Handle filter changes
  const handleFiltersChange = (newFilters: ISearchFilters) => {
    setFilters(newFilters);
    // Auto-search when filters change
    setTimeout(() => performSearch(1), 300);
  };

  // Handle program view
  const handleViewProgram = async (programId: string) => {
    try {
      const program = await api.getProgramDetails(programId);
      setSelectedProgram(program);
      await api.recordInteraction(programId, 'viewed', { source: 'search_results' });
    } catch (error) {
      console.error('Failed to load program details:', error);
    }
  };

  // Handle program save
  const handleSaveProgram = async (programId: string) => {
    try {
      await api.saveProgram(programId);
      await api.recordInteraction(programId, 'saved', { source: 'search_results' });
    } catch (error) {
      console.error('Failed to save program:', error);
    }
  };

  // Handle pagination
  const handlePageChange = (page: number) => {
    performSearch(page);
  };

  return (
    <div className="w-full">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-4 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search for programs, institutions, or fields of study..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search'}
        </Button>
      </form>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          {searchResults && (
            <SearchFilters
              filters={filters}
              onFiltersChange={handleFiltersChange}
              facets={searchResults.facets}
            />
          )}
        </div>

        {/* Search Results */}
        <div className="lg:col-span-3">
          {searchResults && (
            <>
              {/* Results Header */}
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-xl font-semibold">
                    {searchResults.pagination.total_results} programs found
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    Search completed in {searchResults.metadata.search_time_ms}ms
                    {searchResults.metadata.cache_hit && ' (cached)'}
                  </p>
                </div>
              </div>

              {/* Results Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {searchResults.results.map((program) => (
                  <ProgramCard
                    key={program.id}
                    program={program}
                    onSave={handleSaveProgram}
                    onView={handleViewProgram}
                  />
                ))}
              </div>

              {/* Pagination */}
              {searchResults.pagination.total_pages > 1 && (
                <div className="flex justify-center items-center gap-2">
                  <Button
                    variant="outline"
                    disabled={!searchResults.pagination.has_previous}
                    onClick={() => handlePageChange(currentPage - 1)}
                  >
                    Previous
                  </Button>
                  
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      Page {searchResults.pagination.page} of {searchResults.pagination.total_pages}
                    </span>
                  </div>
                  
                  <Button
                    variant="outline"
                    disabled={!searchResults.pagination.has_next}
                    onClick={() => handlePageChange(currentPage + 1)}
                  >
                    Next
                  </Button>
                </div>
              )}
            </>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="flex justify-center items-center py-12">
              <div className="text-center">
                <LoadingSpinner size="lg" />
                <p className="text-muted-foreground">Searching for programs...</p>
              </div>
            </div>
          )}

          {/* Empty State */}
          {searchResults && searchResults.results.length === 0 && !isLoading && (
            <div className="text-center py-12">
              <GraduationCap className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No programs found</h3>
              <p className="text-muted-foreground mb-4">
                Try adjusting your search terms or filters to find more programs.
              </p>
              <Button
                variant="outline"
                onClick={() => {
                  setSearchText('');
                  setFilters({
                    text: '',
                    program_types: [],
                    levels: [],
                    location: {},
                    languages: [],
                    duration: {},
                    budget: { currency: 'CAD' },
                  });
                  performSearch(1);
                }}
              >
                Clear All Filters
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Program Details Modal */}
      {selectedProgram && (
        <ProgramDetails
          program={selectedProgram}
          onClose={() => setSelectedProgram(null)}
          onSave={handleSaveProgram}
        />
      )}
    </div>
  );
};

export default SchoolProgramsSearch;