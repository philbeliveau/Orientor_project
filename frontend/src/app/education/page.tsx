'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import MainLayout from '@/components/layout/MainLayout';
import educationService, { 
  Program, 
  ProgramSearchRequest, 
  SearchMetadata,
  Institution 
} from '@/services/educationService';

// Search and Filter Components inspired by the clean UI design
interface SearchFiltersProps {
  metadata: SearchMetadata | null;
  onSearch: (request: ProgramSearchRequest) => void;
  isLoading: boolean;
}

const SearchFilters: React.FC<SearchFiltersProps> = ({ metadata, onSearch, isLoading }) => {
  const [query, setQuery] = useState('');
  const [selectedInstitutionTypes, setSelectedInstitutionTypes] = useState<string[]>([]);
  const [selectedLevels, setSelectedLevels] = useState<string[]>([]);
  const [selectedCities, setSelectedCities] = useState<string[]>([]);
  const [selectedFields, setSelectedFields] = useState<string[]>([]);
  const [maxTuition, setMaxTuition] = useState<number | undefined>();
  const [minEmploymentRate, setMinEmploymentRate] = useState<number | undefined>();
  const [hollandMatching, setHollandMatching] = useState(true);

  const handleSearch = () => {
    const searchRequest: ProgramSearchRequest = {
      query: query.trim() || undefined,
      institution_types: selectedInstitutionTypes.length > 0 ? selectedInstitutionTypes as any : undefined,
      program_levels: selectedLevels.length > 0 ? selectedLevels as any : undefined,
      cities: selectedCities.length > 0 ? selectedCities : undefined,
      fields_of_study: selectedFields.length > 0 ? selectedFields : undefined,
      max_tuition: maxTuition,
      min_employment_rate: minEmploymentRate,
      holland_matching: hollandMatching,
      user_id: 1, // In production, get from auth context
      limit: 20,
      offset: 0,
    };

    onSearch(searchRequest);
  };

  const clearFilters = () => {
    setQuery('');
    setSelectedInstitutionTypes([]);
    setSelectedLevels([]);
    setSelectedCities([]);
    setSelectedFields([]);
    setMaxTuition(undefined);
    setMinEmploymentRate(undefined);
    setHollandMatching(true);
    
    // Trigger search with cleared filters
    onSearch({
      holland_matching: true,
      user_id: 1,
      limit: 20,
      offset: 0,
    });
  };

  return (
    <div 
      className="w-full p-6 mb-8"
      style={{
        borderRadius: '24px',
        background: '#e0e0e0',
        boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
      }}
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center">
          <div className="w-8 h-8 bg-purple-100 rounded flex items-center justify-center mr-3">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
          </div>
          Search & Filter Programs
        </h2>
      </div>
      
      {/* Main Search Bar - inspired by the clean search in the UI */}
      <div className="mb-6">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by program name, field, or institution..."
            className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="absolute inset-y-0 right-0 px-4 py-2 bg-purple-500 text-white rounded-r-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {/* Filter Grid - Clean card-based layout */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {/* Institution Type */}
        <div className="bg-gray-50 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Institution Type
          </label>
          <div className="space-y-2">
            {metadata?.institution_types.map((type) => (
              <label key={type} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedInstitutionTypes.includes(type)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedInstitutionTypes([...selectedInstitutionTypes, type]);
                    } else {
                      setSelectedInstitutionTypes(selectedInstitutionTypes.filter(t => t !== type));
                    }
                  }}
                  className="mr-3 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                />
                <span className="text-gray-700 capitalize">{type}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Program Level */}
        <div className="bg-gray-50 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Program Level
          </label>
          <div className="space-y-2">
            {metadata?.program_levels.map((level) => (
              <label key={level} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedLevels.includes(level)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedLevels([...selectedLevels, level]);
                    } else {
                      setSelectedLevels(selectedLevels.filter(l => l !== level));
                    }
                  }}
                  className="mr-3 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                />
                <span className="text-gray-700 capitalize">{level}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Cities */}
        <div className="bg-gray-50 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Cities
          </label>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {metadata?.cities.slice(0, 5).map((city) => (
              <label key={city} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedCities.includes(city)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedCities([...selectedCities, city]);
                    } else {
                      setSelectedCities(selectedCities.filter(c => c !== city));
                    }
                  }}
                  className="mr-3 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                />
                <span className="text-gray-700">{city}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Field of Study */}
        <div className="bg-gray-50 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Field of Study
          </label>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {metadata?.fields_of_study.map((field) => (
              <label key={field} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedFields.includes(field)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedFields([...selectedFields, field]);
                    } else {
                      setSelectedFields(selectedFields.filter(f => f !== field));
                    }
                  }}
                  className="mr-3 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                />
                <span className="text-gray-700">{field}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Max Tuition */}
        <div className="bg-gray-50 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Max Tuition (CAD)
          </label>
          <input
            type="number"
            value={maxTuition || ''}
            onChange={(e) => setMaxTuition(e.target.value ? Number(e.target.value) : undefined)}
            placeholder="e.g. 5000"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {/* Min Employment Rate */}
        <div className="bg-gray-50 rounded-lg p-4">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Min Employment Rate (%)
          </label>
          <input
            type="number"
            value={minEmploymentRate || ''}
            onChange={(e) => setMinEmploymentRate(e.target.value ? Number(e.target.value) : undefined)}
            placeholder="e.g. 85"
            min="0"
            max="100"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-gray-900 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Holland Matching Toggle */}
      <div className="bg-blue-50 rounded-lg p-4 mb-6">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={hollandMatching}
            onChange={(e) => setHollandMatching(e.target.checked)}
            className="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <span className="text-gray-900 font-medium">
            Enable personality-based matching (Holland RIASEC)
          </span>
        </label>
        <p className="text-sm text-gray-600 mt-2">
          When enabled, programs are sorted by compatibility with your personality profile
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleSearch}
          disabled={isLoading}
          className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 font-medium transition-colors"
        >
          Apply Filters
        </button>
        <button
          onClick={clearFilters}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
        >
          Clear All
        </button>
      </div>
    </div>
  );
};

// Enhanced Program Card Component with cleaner design inspired by the UI
interface ProgramCardProps {
  program: Program;
  onSave: (programId: string) => void;
  onUnsave: (programId: string) => void;
  isSaved: boolean;
}

const ProgramCard: React.FC<ProgramCardProps> = ({ program, onSave, onUnsave, isSaved }) => {
  const compatibilityPercentage = educationService.calculateCompatibilityPercentage(program.holland_compatibility);
  const topTraits = educationService.getTopHollandTraits(program.holland_compatibility);
  const tuitionFormatted = educationService.formatTuition(program.tuition_domestic, true);

  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="w-full p-6 transition-all duration-300"
      style={{
        borderRadius: '24px',
        background: '#e0e0e0',
        boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
      }}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 mb-2">{program.title}</h3>
          <div className="flex items-center text-gray-600 mb-1">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H9m0 0H5m4 0v-4a1 1 0 011-1h4a1 1 0 011 1v4M7 7h10M7 11h4" />
            </svg>
            {program.institution.name}
          </div>
          <div className="flex items-center text-gray-500 text-sm">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {program.institution.city}, {program.institution.province_state}
          </div>
        </div>
        <div className="text-right">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            program.institution.institution_type === 'cegep' 
              ? 'bg-teal-100 text-teal-800' 
              : program.institution.institution_type === 'university'
              ? 'bg-purple-100 text-purple-800'
              : 'bg-green-100 text-green-800'
          }`}>
            {program.institution.institution_type.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Program Details Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Level</p>
          <p className="font-semibold text-gray-900 capitalize">{program.level}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Duration</p>
          <p className="font-semibold text-gray-900">
            {program.duration_months ? `${program.duration_months} months` : 'Not specified'}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Tuition</p>
          <p className="font-semibold text-gray-900">{tuitionFormatted}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Employment Rate</p>
          <p className="font-semibold text-green-600">
            {program.employment_rate ? `${program.employment_rate}%` : 'N/A'}
          </p>
        </div>
      </div>

      {/* Field of Study */}
      <div className="mb-4">
        <span className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
          {program.field_of_study}
        </span>
      </div>

      {/* Holland Compatibility */}
      {program.holland_compatibility && (
        <div className="mb-4 bg-purple-50 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <p className="text-sm font-medium text-purple-800">Personality Match</p>
            <p className="text-xl font-bold text-purple-600">{compatibilityPercentage}%</p>
          </div>
          <p className="text-sm text-purple-700">
            Best fit for: {topTraits.join(', ')} personalities
          </p>
        </div>
      )}

      {/* Description */}
      <p className="text-gray-600 mb-4 line-clamp-3">{program.description}</p>

      {/* Career Outcomes */}
      {program.career_outcomes.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Career Paths</p>
          <div className="flex flex-wrap gap-2">
            {program.career_outcomes.slice(0, 3).map((outcome, index) => (
              <span 
                key={index}
                className="inline-block bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs"
              >
                {outcome}
              </span>
            ))}
            {program.career_outcomes.length > 3 && (
              <span className="inline-block text-gray-500 px-2 py-1 text-xs">
                +{program.career_outcomes.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => isSaved ? onUnsave(program.id) : onSave(program.id)}
          className={`flex-1 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
            isSaved
              ? 'bg-green-100 text-green-800 border border-green-300'
              : 'bg-purple-500 text-white hover:bg-purple-600'
          }`}
        >
          {isSaved ? '✓ Saved' : 'Save Program'}
        </button>
        <button 
          onClick={() => window.open(program.institution.website_url, '_blank')}
          className="px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
        >
          Learn More
        </button>
      </div>
    </motion.div>
  );
};

// Main Education Page Component
export default function EducationPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [metadata, setMetadata] = useState<SearchMetadata | null>(null);
  const [savedPrograms, setSavedPrograms] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchMetadata, setSearchMetadata] = useState<any>(null);
  const [hasSearched, setHasSearched] = useState(false);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Load search metadata
        const metadataResponse = await educationService.getSearchMetadata();
        setMetadata(metadataResponse);

        // Load personalized recommendations
        const recommendationsResponse = await educationService.getPersonalizedRecommendations(1, 20);
        setPrograms(recommendationsResponse.programs);
        setSearchMetadata(recommendationsResponse.search_metadata);

        // Load saved programs (mock for now)
        setSavedPrograms(['dawson-computer-science']);

      } catch (err) {
        console.error('Error loading initial data:', err);
        setError('Failed to load education programs. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, []);

  const handleSearch = async (searchRequest: ProgramSearchRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      setHasSearched(true);

      const response = await educationService.searchPrograms(searchRequest);
      setPrograms(response.programs);
      setSearchMetadata(response.search_metadata);

    } catch (err) {
      console.error('Error searching programs:', err);
      setError('Failed to search programs. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveProgram = async (programId: string) => {
    try {
      await educationService.saveProgram(programId, 1);
      setSavedPrograms(prev => [...prev, programId]);
    } catch (err) {
      console.error('Error saving program:', err);
    }
  };

  const handleUnsaveProgram = async (programId: string) => {
    try {
      await educationService.unsaveProgram(programId, 1);
      setSavedPrograms(prev => prev.filter(id => id !== programId));
    } catch (err) {
      console.error('Error unsaving program:', err);
    }
  };

  return (
    <MainLayout>
      <div className="relative flex w-full min-h-screen flex-col pb-20 overflow-x-hidden" style={{ backgroundColor: '#ffffff' }}>
        
        <div className="relative z-10 w-full">
          <div className="flex-1 w-full px-4 sm:px-6 md:px-12 lg:px-16 xl:px-24 max-w-none">
            
            {/* Header Section with Dashboard-style design */}
            <div className="flex flex-col gap-6 mb-8">
              <div className="w-full">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* Header Title Card */}
                  <div className="lg:col-span-2">
                    <h1 className="text-2xl font-semibold mb-4" style={{ color: '#000000' }}>Education Programs</h1>
                    <div 
                      className="w-full p-6"
                      style={{
                        borderRadius: '24px',
                        background: '#e0e0e0',
                        boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
                      }}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h2 className="text-lg font-medium text-gray-900">
                            Hey there! 👋
                          </h2>
                          <p className="text-sm text-gray-600 mt-1">
                            It's a great day to explore your educational future!
                          </p>
                        </div>
                        
                        <div className="bg-purple-100 text-purple-600 px-3 py-1 rounded-full text-sm font-medium flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          Personal Match
                        </div>
                      </div>
                      
                      {/* Stats */}
                      <div className="flex gap-4">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl font-bold text-purple-600">
                            {programs.length}
                          </span>
                          <span className="text-sm text-gray-600">
                            programs found
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-2xl font-bold text-green-600">
                            {savedPrograms.length}
                          </span>
                          <span className="text-sm text-gray-600">
                            saved programs
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Quick Stats Card */}
                  <div className="w-full">
                    <h2 className="text-lg font-semibold mb-4 opacity-0">Hidden</h2>
                    <div 
                      className="w-full p-6"
                      style={{
                        height: '200px',
                        borderRadius: '24px',
                        background: '#e0e0e0',
                        boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
                      }}
                    >
                      <h3 className="text-md font-medium text-gray-900 mb-3">Program Types</h3>
                      {metadata && (
                        <div className="space-y-2">
                          {metadata.institution_types.slice(0, 3).map((type, index) => (
                            <div key={index} className="flex items-center justify-between">
                              <span className="text-sm text-gray-700 capitalize">{type}</span>
                              <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-blue-500 h-2 rounded-full" 
                                  style={{ width: `${Math.random() * 100}%` }}
                                ></div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  
                </div>
              </div>
            </div>

          {/* Search and Filters */}
          <SearchFilters 
            metadata={metadata}
            onSearch={handleSearch}
            isLoading={isLoading}
          />

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Content Section with Dashboard-style layout */}
          <div className="flex flex-col lg:grid lg:grid-cols-1 gap-6 mb-8">
            
            {/* Results Header */}
            {searchMetadata && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="w-full"
              >
                <div 
                  className="w-full p-6"
                  style={{
                    borderRadius: '24px',
                    background: '#e0e0e0',
                    boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
                  }}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900 mb-1">
                        {hasSearched ? 'Search Results' : 'Recommended for You'}
                      </h2>
                      <p className="text-sm text-gray-600">
                        {searchMetadata.holland_matching_enabled ? 
                          `Found ${programs.length} programs sorted by personality match` :
                          `Found ${programs.length} programs`
                        }
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-purple-600">{programs.length}</div>
                      <div className="text-xs text-gray-500">Programs Found</div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div 
                className="w-full p-12 text-center"
                style={{
                  borderRadius: '24px',
                  background: '#e0e0e0',
                  boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
                }}
              >
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
                <span className="block mt-3 text-gray-600">Loading programs...</span>
              </div>
            )}

            {/* Programs Grid */}
            {!isLoading && programs.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="grid lg:grid-cols-2 xl:grid-cols-3 gap-6"
              >
                {programs.map((program) => (
                  <ProgramCard
                    key={program.id}
                    program={program}
                    onSave={handleSaveProgram}
                    onUnsave={handleUnsaveProgram}
                    isSaved={savedPrograms.includes(program.id)}
                  />
                ))}
              </motion.div>
            )}
          </div>

          {/* No Results */}
          {!isLoading && programs.length === 0 && hasSearched && (
            <div 
              className="w-full p-12 text-center"
              style={{
                borderRadius: '24px',
                background: '#e0e0e0',
                boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
              }}
            >
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No programs found</h3>
              <p className="text-sm text-gray-600 mb-4">
                Try adjusting your search criteria or removing some filters.
              </p>
            </div>
          )}

          {/* Summary Stats */}
          {searchMetadata && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="w-full"
            >
              <div 
                className="w-full p-6"
                style={{
                  borderRadius: '24px',
                  background: '#e0e0e0',
                  boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
                }}
              >
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Search Summary</h2>
                <div className="grid md:grid-cols-4 gap-6 text-center">
                  <div>
                    <div className="text-2xl font-bold text-purple-600 mb-1">{programs.length}</div>
                    <div className="text-xs text-gray-600">Programs Found</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-600 mb-1">{savedPrograms.length}</div>
                    <div className="text-xs text-gray-600">Programs Saved</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-blue-600 mb-1">
                      {searchMetadata.total_available_programs}
                    </div>
                    <div className="text-xs text-gray-600">Total Available</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-orange-600 mb-1">
                      {searchMetadata.holland_matching_enabled ? 'ON' : 'OFF'}
                    </div>
                    <div className="text-xs text-gray-600">Personality Matching</div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}