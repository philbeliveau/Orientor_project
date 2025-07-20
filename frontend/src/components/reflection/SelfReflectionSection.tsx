'use client';

import React, { useState, useEffect } from 'react';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import reflectionService, { ReflectionQuestion, ReflectionResponse } from '@/services/reflectionService';

interface QuestionWithResponse extends ReflectionQuestion {
  response?: ReflectionResponse;
}

interface SelfReflectionSectionProps {
  className?: string;
}

const SelfReflectionSection: React.FC<SelfReflectionSectionProps> = ({ className = '' }) => {
  const [questions, setQuestions] = useState<QuestionWithResponse[]>([]);
  const [responses, setResponses] = useState<{ [key: number]: string }>({});
  const [editingQuestions, setEditingQuestions] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadQuestionsAndResponses();
  }, []);

  const loadQuestionsAndResponses = async () => {
    try {
      setLoading(true);
      setError(null);
      const questionsWithResponses = await reflectionService.getQuestionsWithResponses();
      setQuestions(questionsWithResponses);
      
      // Initialiser les réponses locales
      const initialResponses: { [key: number]: string } = {};
      questionsWithResponses.forEach(q => {
        if (q.response?.response) {
          initialResponses[q.id] = q.response.response;
        }
      });
      setResponses(initialResponses);
    } catch (err) {
      console.error('Erreur lors du chargement:', err);
      setError('Impossible de charger les questions de réflexion');
    } finally {
      setLoading(false);
    }
  };

  const handleResponseChange = (questionId: number, value: string) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const handleSaveResponse = async (questionId: number) => {
    try {
      setSaving(prev => new Set(prev).add(questionId));
      const response = responses[questionId] || '';
      
      await reflectionService.saveResponse({
        question_id: questionId,
        response: response.trim() || null
      });
      
      // Recharger les données pour avoir les informations à jour
      await loadQuestionsAndResponses();
      setEditingQuestions(prev => {
        const newSet = new Set(prev);
        newSet.delete(questionId);
        return newSet;
      });
    } catch (err) {
      console.error('Erreur lors de la sauvegarde:', err);
      setError('Erreur lors de la sauvegarde de la réponse');
    } finally {
      setSaving(prev => {
        const newSet = new Set(prev);
        newSet.delete(questionId);
        return newSet;
      });
    }
  };

  const handleSaveAll = async () => {
    try {
      setSaving(new Set(questions.map(q => q.id)));
      
      const responsesToSave = questions.map(q => ({
        question_id: q.id,
        response: responses[q.id]?.trim() || null
      }));
      
      await reflectionService.saveResponsesBatch({ responses: responsesToSave });
      await loadQuestionsAndResponses();
      setEditingQuestions(new Set());
    } catch (err) {
      console.error('Erreur lors de la sauvegarde globale:', err);
      setError('Erreur lors de la sauvegarde des réponses');
    } finally {
      setSaving(new Set());
    }
  };

  const toggleEditing = (questionId: number) => {
    setEditingQuestions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(questionId)) {
        newSet.delete(questionId);
      } else {
        newSet.add(questionId);
      }
      return newSet;
    });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Date invalide';
    }
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className={`premium-card p-6 ${className}`}>
        <div className="flex items-center justify-center py-8">
          <div className="premium-spinner"></div>
          <span className="premium-text ml-3">Chargement des questions...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`premium-card p-6 ${className}`}>
        <div className="text-center py-8">
          <p className="premium-text-error mb-4">{error}</p>
          <button 
            onClick={loadQuestionsAndResponses}
            className="premium-button premium-button-primary"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`premium-card p-6 ${className}`}>
      <div className="mb-6">
        <h3 className="premium-section-title mb-2">Self-Reflection</h3>
        <p className="premium-text-secondary">
          Prenez le temps de réfléchir à vos forces et expériences. Ces réflexions vous aideront à mieux comprendre vos talents naturels.
        </p>
      </div>

      {/* Bouton de sauvegarde globale */}
      <div className="mb-6 flex justify-end">
        <button
          onClick={handleSaveAll}
          disabled={saving.size > 0}
          className="premium-button premium-button-primary flex items-center gap-2"
        >
          {saving.size > 0 ? (
            <>
              <LoadingSpinner size="sm" color="white" />
              Sauvegarde...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Sauvegarder tout
            </>
          )}
        </button>
      </div>

      {/* Questions de réflexion */}
      <div className="space-y-6">
        {questions.map((question, index) => {
          const isEditing = editingQuestions.has(question.id);
          const isSaving = saving.has(question.id);
          const hasResponse = question.response?.response;
          const currentResponse = responses[question.id] || '';

          return (
            <div key={question.id} className="premium-card-inner">
              {/* Chat-style header inspiré du template */}
              <div className="relative flex w-full items-center justify-between px-4 py-3 border-b border-gray-200/20">
                <div className="flex items-center gap-3">
                  <div className="premium-nav-icon premium-icon flex items-center justify-center w-8 h-8">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth="1.5"
                      stroke="currentColor"
                      className="w-5 h-5"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M8.625 9.75a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375m-13.5 3.01c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.184-4.183a1.14 1.14 0 0 1 .778-.332 48.294 48.294 0 0 0 5.83-.498c1.585-.233 2.708-1.626 2.708-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"
                      />
                    </svg>
                  </div>
                  <div>
                    <div className="premium-text font-semibold">Question {index + 1}</div>
                    <div className="premium-text-secondary text-sm">{question.category}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {hasResponse && (
                    <span className="premium-badge premium-badge-success text-xs">
                      Répondu
                    </span>
                  )}
                  <button
                    onClick={() => toggleEditing(question.id)}
                    className="premium-button-icon"
                    title={isEditing ? "Annuler l'édition" : "Modifier la réponse"}
                  >
                    {isEditing ? (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* Chat-style content */}
              <div className="p-4">
                {/* Question */}
                <div className="mb-4">
                  <div className="flex flex-col items-start">
                    <div className="premium-text-secondary text-xs mb-1">Question</div>
                    <div className="w-full rounded-lg bg-gradient-to-r from-blue-600/20 to-purple-600/20 px-4 py-3 premium-text">
                      {question.question}
                    </div>
                  </div>
                </div>

                {/* Réponse existante ou zone d'édition */}
                {isEditing ? (
                  <div className="space-y-3">
                    <div className="premium-text-secondary text-xs">Votre réponse</div>
                    <textarea
                      value={currentResponse}
                      onChange={(e) => handleResponseChange(question.id, e.target.value)}
                      placeholder="Partagez votre réflexion..."
                      className="w-full h-32 rounded-lg border border-gray-300/20 bg-gray-100/10 px-4 py-3 premium-text resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    />
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => toggleEditing(question.id)}
                        className="premium-button premium-button-secondary"
                      >
                        Annuler
                      </button>
                      <button
                        onClick={() => handleSaveResponse(question.id)}
                        disabled={isSaving}
                        className="premium-button premium-button-primary flex items-center gap-2"
                      >
                        {isSaving ? (
                          <>
                            <LoadingSpinner size="sm" color="white" />
                            Sauvegarde...
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            Sauvegarder
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ) : hasResponse ? (
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <div className="premium-text-secondary text-xs">Votre réponse</div>
                      <div className="premium-text-secondary text-xs">
                        {formatDate(question.response!.updated_at)}
                      </div>
                    </div>
                    <div className="w-full rounded-lg bg-gray-100/10 px-4 py-3 premium-text">
                      {question.response!.response}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <p className="premium-text-secondary mb-3">Aucune réponse enregistrée</p>
                    <button
                      onClick={() => toggleEditing(question.id)}
                      className="premium-button premium-button-primary"
                    >
                      Commencer la réflexion
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SelfReflectionSection;