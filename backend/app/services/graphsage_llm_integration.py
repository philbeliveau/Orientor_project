"""
GraphSage-Enhanced LLM Integration Service

This service integrates GraphSage relevance scores with LLM conversations to provide
contextualized skill discussions, explanations, and personalized learning priorities.
"""

import os
import sys
import json
import logging
import torch
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
import pickle

# Add the path to import the GNN model
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
from GNN.GraphSage import GraphSAGE, CareerTreeModel

from ..models import User, UserSkill, UserProfile, SavedRecommendation, UserRepresentation

logger = logging.getLogger(__name__)

class GraphSageLLMIntegration:
    """
    Integrates GraphSage relevance scores with LLM conversations for enhanced 
    career guidance and skill explanations.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.gnn_model = None
        self.node_metadata = {}
        self.node_features = None
        self.edge_index = None
        self.node2idx = {}
        self.idx2node = {}
        self._initialize_graphsage_model()
        
    def _initialize_graphsage_model(self):
        """Initialize the GraphSage model and load graph data."""
        try:
            # Load the trained GraphSage model
            model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "services", "GNN", "best_model_20250520_022237.pt"
            )
            
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "dev", "competenceTree_dev", "data"
            )
            
            if os.path.exists(model_path):
                try:
                    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
                    
                    # Initialize model with checkpoint dimensions to avoid size mismatch
                    self.gnn_model = CareerTreeModel(
                        input_dim=checkpoint.get('input_dim', 384),
                        hidden_dim=checkpoint.get('hidden_dim', 128),  # Use 128 to match checkpoint
                        output_dim=checkpoint.get('output_dim', 128),
                        dropout=checkpoint.get('dropout', 0.2)
                    )
                    
                    self.gnn_model.load_state_dict(checkpoint['model_state_dict'])
                    self.gnn_model.eval()
                    logger.info("GraphSage model loaded successfully")
                except Exception as e:
                    logger.error(f"Error loading GraphSage model: {str(e)}")
                    logger.warning("Using fallback method without GNN model")
                    self.gnn_model = None
                    return
            else:
                logger.warning(f"GraphSage model not found at {model_path}, using fallback method")
                self.gnn_model = None
                return
                
            # Load graph data
            self._load_graph_data(data_path)
            
        except Exception as e:
            logger.error(f"Error initializing GraphSage model: {str(e)}")
            
    def _load_graph_data(self, data_path: str):
        """Load graph data including node features, edge index, and metadata."""
        try:
            # Load node metadata
            metadata_path = os.path.join(data_path, "node_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.node_metadata = json.load(f)
                    
            # Load node mappings
            node2idx_path = os.path.join(data_path, "node2idx.json")
            idx2node_path = os.path.join(data_path, "idx2node.json")
            
            if os.path.exists(node2idx_path):
                with open(node2idx_path, 'r') as f:
                    self.node2idx = json.load(f)
                    
            if os.path.exists(idx2node_path):
                with open(idx2node_path, 'r') as f:
                    self.idx2node = json.load(f)
                    
            # Load node features and edge index
            features_path = os.path.join(data_path, "node_features.pt")
            edge_path = os.path.join(data_path, "edge_index.pt")
            
            if os.path.exists(features_path):
                self.node_features = torch.load(features_path, map_location="cpu")
                
            if os.path.exists(edge_path):
                self.edge_index = torch.load(edge_path, map_location="cpu")
                
            logger.info(f"Graph data loaded: {len(self.node_metadata)} nodes, "
                       f"{self.edge_index.shape[1] if self.edge_index is not None else 0} edges")
                       
        except Exception as e:
            logger.error(f"Error loading graph data: {str(e)}")
            
    def compute_skill_relevance_scores(self, user_skills: Dict[str, float], 
                                     career_goals: List[str]) -> Dict[str, float]:
        """
        Compute GraphSage-based relevance scores for skills given user profile and career goals.
        
        Args:
            user_skills: Dictionary mapping skill names to proficiency levels
            career_goals: List of career goals/interests
            
        Returns:
            Dictionary mapping skill/node IDs to relevance scores
        """
        if not self.gnn_model or self.node_features is None:
            logger.warning("GraphSage model not available, returning empty scores")
            return {}
            
        try:
            # Get node embeddings from GraphSage
            with torch.no_grad():
                node_embeddings = self.gnn_model.get_node_embeddings(
                    self.node_features, self.edge_index
                )
                
            # Find nodes matching user skills and career goals
            user_skill_nodes = self._find_matching_nodes(user_skills.keys(), node_type="skill")
            career_goal_nodes = self._find_matching_nodes(career_goals, node_type="occupation")
            
            # Compute relevance scores based on embedding similarities
            relevance_scores = {}
            
            if user_skill_nodes and career_goal_nodes:
                # Calculate average embeddings for user skills and career goals
                user_embedding = self._get_average_embedding(user_skill_nodes, node_embeddings)
                career_embedding = self._get_average_embedding(career_goal_nodes, node_embeddings)
                
                # Compute relevance scores for all skills
                for node_id, metadata in self.node_metadata.items():
                    if metadata.get("type") == "skill":
                        node_idx = self.node2idx.get(node_id)
                        if node_idx is not None:
                            node_emb = node_embeddings[int(node_idx)]
                            
                            # Compute similarity to user skills and career goals
                            user_sim = torch.cosine_similarity(node_emb, user_embedding, dim=0)
                            career_sim = torch.cosine_similarity(node_emb, career_embedding, dim=0)
                            
                            # Combined relevance score
                            relevance_scores[node_id] = float(0.6 * career_sim + 0.4 * user_sim)
                            
            return relevance_scores
            
        except Exception as e:
            logger.error(f"Error computing relevance scores: {str(e)}")
            return {}
            
    def _find_matching_nodes(self, terms: List[str], node_type: str) -> List[str]:
        """Find nodes that match given terms and node type."""
        matching_nodes = []
        
        for node_id, metadata in self.node_metadata.items():
            if metadata.get("type") == node_type:
                label = metadata.get("label", "").lower()
                description = metadata.get("description", "").lower()
                
                for term in terms:
                    term_lower = term.lower()
                    if (term_lower in label or term_lower in description or 
                        any(term_lower in alt.lower() for alt in metadata.get("altlabels", "").split("\n"))):
                        matching_nodes.append(node_id)
                        break
                        
        return matching_nodes
        
    def _get_average_embedding(self, node_ids: List[str], embeddings: torch.Tensor) -> torch.Tensor:
        """Get average embedding for a list of nodes."""
        valid_embeddings = []
        
        for node_id in node_ids:
            node_idx = self.node2idx.get(node_id)
            if node_idx is not None:
                valid_embeddings.append(embeddings[int(node_idx)])
                
        if valid_embeddings:
            return torch.stack(valid_embeddings).mean(dim=0)
        else:
            return torch.zeros(embeddings.shape[1])
            
    async def generate_skill_explanation(self, skill_id: str, relevance_score: float,
                                       user_profile: Dict[str, Any]) -> str:
        """
        Generate personalized explanation for why a skill scored highly for the user.
        
        Args:
            skill_id: The skill node ID
            relevance_score: The GraphSage relevance score
            user_profile: User profile information
            
        Returns:
            Personalized explanation string
        """
        try:
            # Get skill metadata
            skill_metadata = self.node_metadata.get(skill_id, {})
            skill_name = skill_metadata.get("label", "Unknown Skill")
            skill_description = skill_metadata.get("description", "")
            
            # Build user context
            user_context = self._build_user_context(user_profile)
            
            prompt = f"""
You are an expert career counselor explaining why specific skills are relevant for a user's career path.

## Skill Information:
- **Skill Name**: {skill_name}
- **Description**: {skill_description}
- **Relevance Score**: {relevance_score:.3f} (0-1 scale, higher is more relevant)

## User Profile:
{user_context}

## Task:
Explain in 2-3 sentences why this skill scored highly ({relevance_score:.3f}) for this specific user's career path. Be specific about:
1. How this skill connects to their interests/goals
2. Why the GraphSage algorithm identified this as relevant
3. How developing this skill could benefit their career trajectory

Keep the explanation conversational, insightful, and actionable. Focus on the "why" behind the relevance score.
"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert career counselor providing personalized skill explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating skill explanation: {str(e)}")
            return f"This skill ({skill_name}) scored {relevance_score:.3f} relevance for your career path based on your profile and goals."
            
    async def generate_personalized_learning_priorities(self, user_id: int, 
                                                       db: Session) -> Dict[str, Any]:
        """
        Generate personalized learning priorities based on GraphSage scores and user profile.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Dictionary containing learning priorities and recommendations
        """
        try:
            # Get user profile data
            user = db.query(User).filter(User.id == user_id).first()
            user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).first()
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
            if not user or not user_profile:
                return {"error": "User profile not found"}
                
            # Extract user skills and career goals
            user_skill_dict = {}
            if user_skills:
                skill_mapping = {
                    "creativity": "Creativity",
                    "leadership": "Leadership", 
                    "digital_literacy": "Digital Literacy",
                    "critical_thinking": "Critical Thinking",
                    "problem_solving": "Problem Solving",
                    "analytical_thinking": "Analytical Thinking",
                    "attention_to_detail": "Attention to Detail",
                    "collaboration": "Collaboration",
                    "adaptability": "Adaptability",
                    "independence": "Independence",
                    "evaluation": "Evaluation",
                    "decision_making": "Decision Making",
                    "stress_tolerance": "Stress Tolerance"
                }
                
                for skill_key, skill_name in skill_mapping.items():
                    value = getattr(user_skills, skill_key)
                    if value is not None:
                        user_skill_dict[skill_name] = value
                        
            career_goals = []
            if user_profile.career_goals:
                career_goals = [user_profile.career_goals]
            if user_profile.interests:
                career_goals.extend(user_profile.interests.split(","))
                
            # Compute relevance scores
            relevance_scores = self.compute_skill_relevance_scores(user_skill_dict, career_goals)
            
            # Get top skills
            top_skills = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Generate learning priorities
            priorities = {
                "high_impact_skills": [],
                "foundational_skills": [],
                "complementary_skills": [],
                "learning_path": []
            }
            
            for skill_id, score in top_skills:
                skill_metadata = self.node_metadata.get(skill_id, {})
                skill_name = skill_metadata.get("label", "Unknown Skill")
                skill_description = skill_metadata.get("description", "")
                
                skill_info = {
                    "skill_id": skill_id,
                    "name": skill_name,
                    "description": skill_description,
                    "relevance_score": score,
                    "explanation": await self.generate_skill_explanation(
                        skill_id, score, self._build_user_profile_dict(user_profile, user_skills)
                    )
                }
                
                if score > 0.8:
                    priorities["high_impact_skills"].append(skill_info)
                elif score > 0.6:
                    priorities["foundational_skills"].append(skill_info)
                else:
                    priorities["complementary_skills"].append(skill_info)
                    
            # Generate learning path
            priorities["learning_path"] = await self._generate_learning_path(
                priorities, user_profile, user_skills
            )
            
            return priorities
            
        except Exception as e:
            logger.error(f"Error generating learning priorities: {str(e)}")
            return {"error": f"Failed to generate learning priorities: {str(e)}"}
            
    async def enhance_conversation_with_graphsage(self, user_message: str, user_id: int,
                                                db: Session) -> Dict[str, Any]:
        """
        Enhance LLM conversation with GraphSage insights and skill relevance.
        
        Args:
            user_message: User's input message
            user_id: User ID
            db: Database session
            
        Returns:
            Enhanced conversation context with GraphSage insights
        """
        try:
            # Get user profile
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).first()
            
            if not user_profile:
                return {"graphsage_insights": "User profile not available"}
                
            # Extract career-related keywords from user message
            career_keywords = self._extract_career_keywords(user_message)
            
            # Get relevant skills based on message context
            user_skill_dict = {}
            if user_skills:
                skill_mapping = {
                    "creativity": "Creativity",
                    "leadership": "Leadership",
                    "digital_literacy": "Digital Literacy", 
                    "critical_thinking": "Critical Thinking",
                    "problem_solving": "Problem Solving"
                }
                
                for skill_key, skill_name in skill_mapping.items():
                    value = getattr(user_skills, skill_key)
                    if value is not None:
                        user_skill_dict[skill_name] = value
                        
            # Compute relevance scores for message context
            relevance_scores = self.compute_skill_relevance_scores(
                user_skill_dict, career_keywords
            )
            
            # Get top relevant skills
            top_skills = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Build GraphSage insights
            insights = {
                "relevant_skills": [],
                "skill_gaps": [],
                "conversation_context": {},
                "learning_suggestions": []
            }
            
            for skill_id, score in top_skills:
                if score > 0.5:  # Only include reasonably relevant skills
                    skill_metadata = self.node_metadata.get(skill_id, {})
                    skill_name = skill_metadata.get("label", "Unknown Skill")
                    
                    insights["relevant_skills"].append({
                        "name": skill_name,
                        "relevance_score": score,
                        "description": skill_metadata.get("description", "")
                    })
                    
            # Provide conversation enhancement context
            insights["conversation_context"] = {
                "user_strengths": [skill for skill, score in user_skill_dict.items() if score >= 4],
                "career_keywords_detected": career_keywords,
                "top_skill_matches": [skill["name"] for skill in insights["relevant_skills"][:3]]
            }
            
            return {"graphsage_insights": insights}
            
        except Exception as e:
            logger.error(f"Error enhancing conversation with GraphSage: {str(e)}")
            return {"graphsage_insights": "GraphSage insights not available"}
            
    def _extract_career_keywords(self, message: str) -> List[str]:
        """Extract career-related keywords from user message."""
        # Simple keyword extraction - could be enhanced with NLP
        career_keywords = []
        
        # Common career-related terms
        career_terms = [
            "career", "job", "work", "profession", "role", "position",
            "skill", "ability", "talent", "expertise", "competence",
            "goal", "ambition", "aspiration", "future", "path"
        ]
        
        message_lower = message.lower()
        for term in career_terms:
            if term in message_lower:
                career_keywords.append(term)
                
        return career_keywords
        
    def _build_user_context(self, user_profile: Dict[str, Any]) -> str:
        """Build user context string for prompts."""
        context_parts = []
        
        if user_profile.get("career_goals"):
            context_parts.append(f"Career Goals: {user_profile['career_goals']}")
        if user_profile.get("interests"):
            context_parts.append(f"Interests: {user_profile['interests']}")
        if user_profile.get("skills"):
            context_parts.append(f"Current Skills: {', '.join(user_profile['skills'])}")
        if user_profile.get("experience_level"):
            context_parts.append(f"Experience Level: {user_profile['experience_level']}")
            
        return "\n".join(context_parts) if context_parts else "Limited profile information available"
        
    def _build_user_profile_dict(self, user_profile, user_skills) -> Dict[str, Any]:
        """Build user profile dictionary for processing."""
        profile_dict = {}
        
        if user_profile:
            profile_dict["career_goals"] = user_profile.career_goals
            profile_dict["interests"] = user_profile.interests
            profile_dict["name"] = user_profile.name
            profile_dict["age"] = user_profile.age
            profile_dict["major"] = user_profile.major
            profile_dict["experience_level"] = user_profile.years_experience
            
        if user_skills:
            profile_dict["skills"] = [
                f"Creativity: {user_skills.creativity}/5",
                f"Leadership: {user_skills.leadership}/5",
                f"Digital Literacy: {user_skills.digital_literacy}/5",
                f"Critical Thinking: {user_skills.critical_thinking}/5",
                f"Problem Solving: {user_skills.problem_solving}/5"
            ]
            
        return profile_dict
        
    async def _generate_learning_path(self, priorities: Dict[str, Any], 
                                    user_profile, user_skills) -> List[Dict[str, Any]]:
        """Generate a structured learning path based on priorities."""
        try:
            # Build context for learning path generation
            context = self._build_user_context(
                self._build_user_profile_dict(user_profile, user_skills)
            )
            
            high_impact = priorities.get("high_impact_skills", [])
            foundational = priorities.get("foundational_skills", [])
            
            prompt = f"""
Based on the user's profile and high-impact skills identified by GraphSage analysis, create a structured 6-month learning path.

## User Context:
{context}

## High-Impact Skills (GraphSage Score > 0.8):
{json.dumps([{"name": skill["name"], "score": skill["relevance_score"]} for skill in high_impact], indent=2)}

## Foundational Skills (GraphSage Score > 0.6):
{json.dumps([{"name": skill["name"], "score": skill["relevance_score"]} for skill in foundational], indent=2)}

Create a learning path with:
1. Month 1-2: Foundation building (1-2 skills)
2. Month 3-4: Core skill development (2-3 skills)
3. Month 5-6: Advanced application (1-2 skills)

For each phase, provide:
- Skills to focus on
- Learning objectives
- Recommended resources/activities
- Success metrics

Return as a JSON array of learning phases.
"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert learning path designer creating structured skill development plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Try to parse JSON response
            try:
                learning_path = json.loads(response.choices[0].message.content)
                return learning_path
            except json.JSONDecodeError:
                # Fallback to structured text response
                return [{"phase": "Generated Learning Path", "content": response.choices[0].message.content}]
                
        except Exception as e:
            logger.error(f"Error generating learning path: {str(e)}")
            return [{"phase": "Error", "content": "Unable to generate learning path at this time"}]


# Global instance
graphsage_llm = GraphSageLLMIntegration()