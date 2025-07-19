'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import ExtremeCompetenceTreeView from '../../components/tree/extreme/ExtremeCompetenceTreeView';
import MainLayout from '../../components/layout/MainLayout';
import { generateCompetenceTree } from '../../services/competenceTreeService';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

interface ProfileResponse {
  id: number;
  email?: string;
}

const CompetenceTreePage: React.FC = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // Get graphId from URL params or try to restore from localStorage
  const urlGraphId = searchParams ? searchParams.get('graph_id') : null;
  const [currentGraphId, setCurrentGraphId] = useState<string | null>(urlGraphId);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-restore last viewed tree if no graphId in URL
  useEffect(() => {
    if (urlGraphId) {
      localStorage.setItem('last-competence-tree-id', urlGraphId);
      setCurrentGraphId(urlGraphId);
    }
  }, [urlGraphId]);
  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  // Fonction pour générer un nouvel arbre
  const handleGenerateTree = async () => {
    console.log("handleGenerateTree: Début de la génération de l'arbre");
    try {
      setLoading(true);
      setError(null); // Clear any previous errors
      console.log("handleGenerateTree: Loading state set to true");
      
      // Get the current user's ID from the JWT token
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error("No authentication token found");
        setError("Vous devez être connecté pour générer un arbre de compétences");
        setLoading(false);
        router.push('/login');
        return;
      }

      // Get the user's ID from the email
      console.log('🔍 API_URL being used:', API_URL);
      console.log('🌐 Environment variable NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
      console.log('📡 Full request URL:', `${API_URL}/api/v1/profiles/me`);
      
      console.log('🔐 Token exists:', !!token);
      console.log('🎯 Making request to:', `${API_URL}/api/v1/profiles/me`);
      
      const response = await axios.get<ProfileResponse>(`${API_URL}/api/v1/profiles/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('✅ Response received:', response.status, response.data);
      
      const userId = response.data.id;
      console.log('💾 Saving userId to localStorage:', userId);
      localStorage.setItem('user_id', userId.toString());
      
      console.log('🌳 Generating competence tree for userId:', userId);
      const result = await generateCompetenceTree(userId);
      console.log('🎯 Tree generation result:', result);
      
      // Save as last viewed tree and update state
      localStorage.setItem('last-competence-tree-id', result.graph_id);
      setCurrentGraphId(result.graph_id);
      
      // Rediriger vers la même page avec le graph_id en paramètre
      const newUrl = `/competence-tree?graph_id=${result.graph_id}`;
      router.push(newUrl);
    } catch (err: any) {
      console.error("❌ handleGenerateTree: Erreur lors de la génération:", err);
      console.error("❌ Error details:", {
        message: err.message,
        status: err.response?.status,
        statusText: err.response?.statusText,
        url: err.config?.url,
        method: err.config?.method
      });
      
      if (err.response?.status === 401 || err.response?.status === 403) {
        setError("Votre session a expiré. Veuillez vous reconnecter.");
        router.push('/login');
      } else if (err.response?.status === 404) {
        setError(`API endpoint not found: ${err.config?.url}. Please check if the backend is running.`);
      } else {
        setError(err.message || 'Une erreur est survenue lors de la génération de l\'arbre');
      }
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="container">
        {!currentGraphId ? (
          <div className="generate-tree-container" style={{ textAlign: 'center', padding: '50px' }}>
            <h2>Arbre de Compétences</h2>
            <p>Vous n'avez pas encore d'arbre de compétences. Générez-en un pour commencer!</p>
            <button
              onClick={handleGenerateTree}
              disabled={loading}
              style={{
                padding: '15px 30px',
                backgroundColor: loading ? '#95a5a6' : '#2196f3',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.8 : 1,
                fontSize: '16px',
                fontWeight: '500',
                transition: 'all 0.3s ease'
              }}
            >
              {loading ? '🧠 Analyzing your profile...' : '🌳 Generate My Skill Tree'}
            </button>
            {loading && (
              <div style={{ marginTop: '15px', textAlign: 'center' }}>
                <p style={{ color: '#666', fontSize: '14px' }}>
                  🤖 AI is analyzing your profile and building your personalized skill tree...
                </p>
                <p style={{ color: '#888', fontSize: '12px', marginTop: '5px' }}>
                  This may take 1-3 minutes due to the complexity of graph analysis.
                </p>
              </div>
            )}
            {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
          </div>
        ) : (
          <ExtremeCompetenceTreeView graphId={currentGraphId} />
        )}
      </div>
    </MainLayout>
  );
};

export default CompetenceTreePage;
