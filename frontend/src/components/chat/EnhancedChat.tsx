/**
 * Enhanced Chat Component with GraphSage Integration
 * 
 * This component provides an enhanced chat experience with GraphSage-powered
 * skill relevance analysis and personalized learning recommendations.
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface SkillRelevanceInfo {
  name: string;
  relevance_score: number;
  description: string;
}

interface GraphSageInsights {
  relevant_skills: SkillRelevanceInfo[];
  skill_gaps: SkillRelevanceInfo[];
  conversation_context: {
    user_strengths: string[];
    career_keywords_detected: string[];
    top_skill_matches: string[];
  };
  learning_suggestions: string[];
}

interface EnhancedChatMessage {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  graphsage_insights?: GraphSageInsights;
}

interface LearningRecommendation {
  skill_name: string;
  relevance_score: number;
  explanation: string;
}

const EnhancedChat: React.FC = () => {
  const [messages, setMessages] = useState<EnhancedChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [showInsights, setShowInsights] = useState(true);
  const [learningRecommendations, setLearningRecommendations] = useState<LearningRecommendation[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check system status on component mount
    checkSystemStatus();
    
    // Add initial welcome message
    setMessages([{
      id: 0,
      text: "Hello! I'm your enhanced AI career mentor, powered by GraphSage neural network analysis. I can provide personalized insights about skill relevance and career pathways. What would you like to explore today?",
      isUser: false,
      timestamp: new Date()
    }]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const checkSystemStatus = async () => {
    try {
      const response = await fetch('/api/v1/enhanced-chat/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const status = await response.json();
      setSystemStatus(status);
    } catch (error) {
      console.error('Error checking system status:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: EnhancedChatMessage = {
      id: messages.length + 1,
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/enhanced-chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          text: inputText,
          conversation_id: conversationId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      const aiMessage: EnhancedChatMessage = {
        id: data.message_id,
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        graphsage_insights: data.graphsage_insights?.graphsage_insights
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: EnhancedChatMessage = {
        id: messages.length + 2,
        text: "Sorry, I encountered an error. Please try again.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadLearningRecommendations = async () => {
    try {
      const response = await fetch('/api/v1/enhanced-chat/learning-recommendations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        const recommendations = [
          ...data.high_impact_skills,
          ...data.foundational_skills
        ].slice(0, 5); // Top 5 recommendations
        
        setLearningRecommendations(recommendations);
      }
    } catch (error) {
      console.error('Error loading learning recommendations:', error);
    }
  };

  const explainSkill = async (skillName: string) => {
    try {
      const response = await fetch('/api/v1/enhanced-chat/skill-explanation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ skill_name: skillName })
      });

      if (response.ok) {
        const data = await response.json();
        const explanationMessage: EnhancedChatMessage = {
          id: messages.length + 1,
          text: `**${data.skill_name}** (Relevance: ${(data.relevance_score * 100).toFixed(1)}%)\n\n${data.explanation}`,
          isUser: false,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, explanationMessage]);
      }
    } catch (error) {
      console.error('Error explaining skill:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score > 0.8) return 'bg-green-100 text-green-800';
    if (score > 0.6) return 'bg-yellow-100 text-yellow-800';
    if (score > 0.4) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b p-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold">Enhanced Career Chat</h1>
              <p className="text-sm text-gray-600">
                Powered by GraphSage Neural Network Analysis
              </p>
            </div>
            {systemStatus && (
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${systemStatus.enhanced_chat_available ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-600">
                  {systemStatus.enhanced_chat_available ? 'Enhanced Chat Active' : 'Basic Chat Only'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-2xl p-4 rounded-lg ${
                message.isUser 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-white border shadow-sm'
              }`}>
                <div className="prose prose-sm">
                  {message.text.split('\n').map((line, index) => (
                    <p key={index} className={message.isUser ? 'text-white' : ''}>
                      {line.startsWith('**') && line.endsWith('**') ? (
                        <strong>{line.slice(2, -2)}</strong>
                      ) : line}
                    </p>
                  ))}
                </div>
                
                {/* GraphSage Insights */}
                {message.graphsage_insights && showInsights && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">
                      GraphSage Insights
                    </h4>
                    
                    {message.graphsage_insights.relevant_skills.length > 0 && (
                      <div className="mb-2">
                        <p className="text-xs text-gray-600 mb-1">Relevant Skills:</p>
                        <div className="flex flex-wrap gap-1">
                          {message.graphsage_insights.relevant_skills.slice(0, 3).map((skill, index) => (
                            <Badge 
                              key={index} 
                              className={`text-xs cursor-pointer ${getRelevanceColor(skill.relevance_score)}`}
                              onClick={() => explainSkill(skill.name)}
                            >
                              {skill.name} ({(skill.relevance_score * 100).toFixed(0)}%)
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {message.graphsage_insights.conversation_context.user_strengths.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-600 mb-1">Your Strengths:</p>
                        <div className="flex flex-wrap gap-1">
                          {message.graphsage_insights.conversation_context.user_strengths.map((strength, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {strength}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                <div className="text-xs opacity-70 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border rounded-lg p-4 shadow-sm">
                <div className="flex items-center space-x-2">
                  <LoadingSpinner size="sm" />
                  <span className="text-sm text-gray-600">Analyzing with GraphSage...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t bg-white p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about skills, career paths, or learning recommendations..."
              className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <Button 
              onClick={sendMessage} 
              disabled={isLoading || !inputText.trim()}
              className="px-6"
            >
              Send
            </Button>
          </div>
        </div>
      </div>

      {/* Insights Sidebar */}
      {showInsights && (
        <div className="w-80 bg-white border-l overflow-y-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">AI Insights</h2>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setShowInsights(false)}
              >
                Hide
              </Button>
            </div>

            {/* System Status */}
            {systemStatus && (
              <Card className="mb-4">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">System Status</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span>GraphSage Model:</span>
                      <span className={systemStatus.graphsage_model_loaded ? 'text-green-600' : 'text-red-600'}>
                        {systemStatus.graphsage_model_loaded ? 'Loaded' : 'Not Available'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Knowledge Nodes:</span>
                      <span>{systemStatus.node_metadata_count?.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Skill Connections:</span>
                      <span>{systemStatus.edge_count?.toLocaleString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Quick Actions */}
            <Card className="mb-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="pt-0 space-y-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full text-xs"
                  onClick={loadLearningRecommendations}
                >
                  Get Learning Recommendations
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full text-xs"
                  onClick={() => setInputText("What skills should I focus on for my career goals?")}
                >
                  Skill Priority Analysis
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full text-xs"
                  onClick={() => setInputText("Analyze my compatibility with software engineering")}
                >
                  Career Path Analysis
                </Button>
              </CardContent>
            </Card>

            {/* Learning Recommendations */}
            {learningRecommendations.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Top Learning Priorities</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    {learningRecommendations.map((rec, index) => (
                      <div 
                        key={index}
                        className="p-2 bg-gray-50 rounded cursor-pointer hover:bg-gray-100"
                        onClick={() => explainSkill(rec.skill_name)}
                      >
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium">{rec.skill_name}</span>
                          <Badge className={`text-xs ${getRelevanceColor(rec.relevance_score)}`}>
                            {(rec.relevance_score * 100).toFixed(0)}%
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-600 line-clamp-2">
                          {rec.explanation}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Show Insights Button (when hidden) */}
      {!showInsights && (
        <div className="fixed right-4 top-20">
          <Button onClick={() => setShowInsights(true)}>
            Show Insights
          </Button>
        </div>
      )}
    </div>
  );
};

export default EnhancedChat;