import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from pinecone import Pinecone

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Pinecone
PINECONE_INDEX = "esco-368"

class JobRecommendationService:
    """
    Service pour générer des recommandations d'emploi basées sur les embeddings ESCO des utilisateurs.
    """
    
    def __init__(self):
        """
        Initialise le service de recommandation d'emploi.
        """
        self.pinecone_client = None
        self.index = None
        self._initialize_pinecone()
    
    def _initialize_pinecone(self) -> bool:
        """
        Initialise la connexion à Pinecone.
        
        Returns:
            bool: True si l'initialisation a réussi, False sinon
        """
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                logger.error("Clé API Pinecone non définie dans les variables d'environnement")
                return False
            
            self.pinecone_client = Pinecone(api_key=api_key)
            self.index = self.pinecone_client.Index(PINECONE_INDEX)
            logger.info(f"Connexion à l'index Pinecone '{PINECONE_INDEX}' établie avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Pinecone: {str(e)}")
            return False
            
    def _convert_score_to_similarity(self, score: float) -> float:
        """
        Convertit un score de distance Pinecone en score de similarité.
        
        Args:
            score: Score de distance Pinecone
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        # Pinecone retourne une distance, nous la convertissons en similarité (1 - distance)
        return 1.0 - score
    
    def get_user_embedding(self, db: Session, user_id: int, embedding_type: str = "esco_embedding") -> Optional[np.ndarray]:
        """
        Récupère l'embedding ESCO d'un utilisateur depuis la base de données.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            embedding_type: Type d'embedding à récupérer (par défaut: esco_embedding)
            
        Returns:
            np.ndarray: Embedding de l'utilisateur ou None en cas d'échec
        """
        try:
            # Vérifier que le type d'embedding est valide
            valid_types = ["esco_embedding", "esco_embedding_occupation", "esco_embedding_skill", "esco_embedding_skillsgroup"]
            if embedding_type not in valid_types:
                logger.error(f"Type d'embedding invalide: {embedding_type}")
                return None
            
            # Récupérer l'embedding depuis la base de données
            query = text(f"SELECT {embedding_type} FROM user_profiles WHERE user_id = :user_id")
            result = db.execute(query, {"user_id": user_id}).fetchone()
            
            if not result or not result[0]:
                logger.error(f"Aucun embedding {embedding_type} trouvé pour l'utilisateur {user_id}")
                return None
            
            # Convertir la chaîne en tableau numpy
            import ast
            embedding = np.array(ast.literal_eval(result[0]), dtype=np.float32)
            logger.info(f"Embedding {embedding_type} récupéré avec succès pour l'utilisateur {user_id}: {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'embedding: {str(e)}")
            return None
    
    def query_job_recommendations(self, embedding: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Interroge l'index Pinecone pour obtenir les recommandations d'emploi.
        
        Args:
            embedding: Embedding de l'utilisateur
            top_k: Nombre de recommandations à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des recommandations d'emploi
        """
        try:
            if self.index is None:
                if not self._initialize_pinecone():
                    logger.error("Impossible d'initialiser Pinecone")
                    return []
            
            # Convertir l'embedding en liste
            vector = embedding.tolist()
            
            # Interroger Pinecone pour les occupations uniquement
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter={"type": {"$eq": "occupation"}},
                include_metadata=True
            )
            
            # Formater les résultats
            recommendations = []
            for match in results.matches:
                similarity = self._convert_score_to_similarity(match.score)
                recommendation = {
                    "id": match.id,
                    "score": similarity,
                    "metadata": match.metadata
                }
                recommendations.append(recommendation)
            
            # Log only relevant information
            logger.info(f"📊 Retrieved {len(recommendations)} job recommendations")
            for i, rec in enumerate(recommendations):
                logger.info(f"  {i+1}. {rec['metadata'].get('title', rec['metadata'].get('preferred_label', 'Unknown'))} (score: {rec['score']:.2f})")
            
            return recommendations
        except Exception as e:
            logger.error(f"❌ Error querying Pinecone: {str(e)}")
            return []
    
    def store_recommendations(self, db: Session, user_id: int, recommendations: List[Dict[str, Any]]) -> bool:
        """
        Stocke les recommandations d'emploi dans la base de données.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            recommendations: Liste des recommandations d'emploi
            
        Returns:
            bool: True si le stockage a réussi, False sinon
        """
        try:
            # Convertir les recommandations en JSON
            import json
            recommendations_json = json.dumps(recommendations)
            
            # Mettre à jour la base de données
            query = text("""
                UPDATE user_profiles
                SET top3_recommendedJobs = :recommendations
                WHERE user_id = :user_id
            """)
            db.execute(query, {"user_id": user_id, "recommendations": recommendations_json})
            db.commit()
            
            logger.info(f"Recommandations stockées avec succès pour l'utilisateur {user_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du stockage des recommandations: {str(e)}")
            db.rollback()
            return False
    
    def get_job_recommendations(self, db: Session, user_id: int, embedding_type: str = "esco_embedding", top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Obtient les recommandations d'emploi pour un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            embedding_type: Type d'embedding à utiliser
            top_k: Nombre de recommandations à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des recommandations d'emploi
        """
        try:
            # Récupérer l'embedding de l'utilisateur
            embedding = self.get_user_embedding(db, user_id, embedding_type)
            if embedding is None:
                logger.error(f"❌ No embedding found for user {user_id}")
                return []
            
            # Interroger Pinecone pour les recommandations
            recommendations = self.query_job_recommendations(embedding, top_k)
            if not recommendations:
                logger.warning(f"⚠️ No recommendations found for user {user_id}")
                return []
            
            # Stocker les recommandations
            self.store_recommendations(db, user_id, recommendations)
            
            return recommendations
        except Exception as e:
            logger.error(f"❌ Error getting job recommendations: {str(e)}")
            return []
    
    def generate_skill_tree_for_job(self, job_id: str, depth: int = 1, max_nodes: int = 5) -> Dict[str, Any]:
        """
        Génère un arbre de compétences pour un emploi spécifique.
        
        Args:
            job_id: ID de l'emploi (format: 'occupation::key_XXXXX')
            depth: Profondeur de l'arbre (1-3)
            max_nodes: Nombre maximum de nœuds par niveau (3-10)
            
        Returns:
            Dict[str, Any]: Arbre de compétences généré avec visualisation
        """
        try:
            # Add the dev directory to the Python path temporarily
            import sys
            import os
            dev_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'dev')
            if dev_path not in sys.path:
                sys.path.append(dev_path)
            
            from competenceTree_dev.graph_traversal_service import GraphTraversalService
            from competenceTree_dev.skill_tree_visualization import SkillTreeVisualization
            
            # Valider les paramètres
            depth = max(1, min(3, depth))  # Limiter entre 1 et 3
            max_nodes = max(3, min(10, max_nodes))  # Limiter entre 3 et 10
            
            # Initialiser le service de traversée du graphe
            graph_service = GraphTraversalService()
            
            # Initialiser le service de visualisation
            viz_service = SkillTreeVisualization()
            
            # Vérifier si le nœud d'emploi existe dans le graphe
            if job_id not in graph_service.graph.nodes:
                logger.error(f"L'ID d'emploi {job_id} n'existe pas dans le graphe")
                return {}
            
            # Récupérer les informations sur l'emploi
            job_info = graph_service.get_node_info(job_id)
            if not job_info:
                logger.error(f"Impossible de récupérer les informations pour l'emploi {job_id}")
                return {}
            
            # Traverser le graphe à partir de l'ID de l'emploi avec les paramètres spécifiés
            graph_data = graph_service.traverse_graph(
                anchor_node_ids=[job_id],
                max_depth=depth,  # Profondeur spécifiée par l'utilisateur
                min_similarity=0.7,
                max_nodes_per_level=max_nodes  # Nombre de nœuds spécifié par l'utilisateur
            )
            
            logger.info(f"Arbre de compétences généré avec profondeur={depth} et max_nodes={max_nodes}")
            
            if not graph_data.get("nodes"):
                logger.error(f"Aucun nœud trouvé lors de la traversée du graphe pour l'emploi {job_id}")
                return {}
            
            # Générer une visualisation de l'arbre de compétences
            try:
                # Créer une visualisation Plotly interactive
                plotly_viz = viz_service.visualize_plotly(graph_data)
                
                # Créer une visualisation Matplotlib statique
                matplotlib_viz = viz_service.visualize_matplotlib(graph_data)
                
                # Créer une visualisation pour Streamlit
                streamlit_viz = viz_service.create_streamlit_visualization(graph_data)
                
                # Ajouter les visualisations au graphe
                graph_data["visualizations"] = {
                    "plotly": plotly_viz,
                    "matplotlib": matplotlib_viz,
                    "streamlit": streamlit_viz
                }
                
                # Logs détaillés pour déboguer les visualisations
                logger.info("=== DÉTAILS DES VISUALISATIONS ===")
                logger.info(f"Visualisation Plotly disponible: {plotly_viz is not None}")
                if plotly_viz:
                    logger.info(f"Type de visualisation Plotly: {type(plotly_viz)}")
                    logger.info(f"Clés de visualisation Plotly: {plotly_viz.keys() if isinstance(plotly_viz, dict) else 'N/A'}")
                
                logger.info(f"Visualisation Matplotlib disponible: {matplotlib_viz is not None}")
                if matplotlib_viz:
                    logger.info(f"Type de visualisation Matplotlib: {type(matplotlib_viz)}")
                    logger.info(f"Longueur de la chaîne base64: {len(matplotlib_viz) if isinstance(matplotlib_viz, str) else 'N/A'}")
                
                logger.info(f"Visualisation Streamlit disponible: {streamlit_viz is not None}")
                if streamlit_viz:
                    logger.info(f"Type de visualisation Streamlit: {type(streamlit_viz)}")
                    logger.info(f"Clés de visualisation Streamlit: {streamlit_viz.keys() if isinstance(streamlit_viz, dict) else 'N/A'}")
                logger.info("=== FIN DES DÉTAILS DES VISUALISATIONS ===")
                
                logger.info("Visualisations de l'arbre de compétences générées avec succès")
            except Exception as viz_error:
                logger.error(f"Erreur lors de la génération des visualisations: {str(viz_error)}")
                # Continuer même si la visualisation échoue
            
            logger.info(f"Arbre de compétences généré avec succès pour l'emploi {job_id}")
            return graph_data
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'arbre de compétences: {str(e)}")
            return {}
            
    def get_stored_recommendations(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Récupère les recommandations d'emploi stockées pour un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            List[Dict[str, Any]]: Liste des recommandations d'emploi stockées
        """
        try:
            # Récupérer les recommandations depuis la base de données
            query = text("SELECT top3_recommendedJobs FROM user_profiles WHERE user_id = :user_id")
            result = db.execute(query, {"user_id": user_id}).fetchone()
            
            if not result or not result[0]:
                logger.info(f"Aucune recommandation stockée pour l'utilisateur {user_id}")
                return []
            
            # Convertir la chaîne JSON en liste de dictionnaires
            import json
            recommendations = json.loads(result[0])
            logger.info(f"Recommandations récupérées avec succès pour l'utilisateur {user_id}")
            return recommendations
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des recommandations stockées: {str(e)}")
            return []