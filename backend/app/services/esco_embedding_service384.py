import os
import logging
import importlib.util
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
import torch
from torch_geometric.data import Data
import sys
from pathlib import Path
from app.services.GNN.GraphSage import GraphSAGE, CareerTreeModel


# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import du module de formatage ESCO
def import_esco_formatter():
    """
    Importe dynamiquement le module de formatage ESCO.
    
    Returns:
        Le module importé ou None en cas d'échec
    """
    try:
        # Chemin vers le module de formatage ESCO
        # Le module se trouve dans le répertoire 'scripts' au niveau racine du projet
        # From app/services/esco_embedding_service384.py -> backend/scripts/
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                  "scripts", "format_user_profile_esco_style.py")
        
        # Vérifier si le fichier existe
        if not os.path.exists(script_path):
            logger.error(f"Le module de formatage ESCO n'existe pas au chemin: {script_path}")
            logger.info(f"Chemin absolu recherché: {os.path.abspath(script_path)}")
            return None
            
        # Importer le module dynamiquement
        spec = importlib.util.spec_from_file_location("format_user_profile_esco_style", script_path)
        esco_formatter = importlib.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(esco_formatter)
            
            # Vérifier si le module a les dépendances requises
            if hasattr(esco_formatter, "check_dependencies"):
                if not esco_formatter.check_dependencies():
                    logger.error("Le module de formatage ESCO a des dépendances manquantes")
                    return None
            
            logger.info("Module de formatage ESCO importé avec succès")
            return esco_formatter
        except ImportError as e:
            logger.error(f"Erreur d'importation lors du chargement du module ESCO: {str(e)}")
            logger.info("Certaines dépendances requises peuvent être manquantes. Vérifiez que tous les packages nécessaires sont installés.")
            return None
    except Exception as e:
        logger.error(f"Erreur lors de l'importation du module de formatage ESCO: {str(e)}")
        return None

# Importer le module de formatage ESCO
esco_formatter = import_esco_formatter()

# Importer le service d'embedding existant
from app.services.Oasisembedding_service import (
    model_state, fetch_user_data, generate_embedding_from_text_384, store_embedding
)

# Chemin vers le modèle GraphSAGE préentraîné
GRAPHSAGE_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # This will point to the backend/app directory
    "services",
    "GNN",  # The directory where the model is located
    "pause_checkpoint_20250519_113135.pt"  # The model file
)

# Vérifier si le modèle GraphSAGE existe
if not os.path.exists(GRAPHSAGE_MODEL_PATH):
    logger.error(f"Le modèle GraphSAGE n'existe pas au chemin: {GRAPHSAGE_MODEL_PATH}")
    logger.info(f"Chemin absolu recherché: {os.path.abspath(GRAPHSAGE_MODEL_PATH)}")

# Ajouter le chemin des modèles au sys.path
models_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # This will point to the backend/app directory
    "GNN"  # The directory where the model is located
)
if models_path not in sys.path:
    sys.path.append(models_path)

# Add the path to the GNN directory
gnn_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GNN")
if gnn_path not in sys.path:
    sys.path.append(gnn_path)


class GraphSAGEModelState:
    def __init__(self):
        self.model = None  # This will hold encoder (GraphSAGE)
        self.model_loaded = False

    def load_model(self) -> bool:
        if self.model_loaded:
            return True

        try:
            # Instantiate full CareerTreeModel
            full_model = CareerTreeModel(
                input_dim=1024,
                hidden_dim=128,
                output_dim=128,
                dropout=0.2
            )

            # Load checkpoint from training
            checkpoint = torch.load(GRAPHSAGE_MODEL_PATH, map_location="cpu", weights_only=False)

            # Extract model_state_dict and load into full model
            if "model_state_dict" not in checkpoint:
                logger.error("❌ Le checkpoint ne contient pas 'model_state_dict'")
                return False

            full_model.load_state_dict(checkpoint["model_state_dict"])
            full_model.eval()

            # ✅ Store only the encoder (GraphSAGE)
            self.model = full_model.encoder
            self.model.eval()
            self.model_loaded = True

            logger.info("✅ Modèle GraphSAGE (encoder) chargé avec succès depuis CareerTreeModel")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du modèle GraphSAGE depuis CareerTreeModel: {str(e)}")
            return False

    
    def project_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """
        Projette un embedding de 1024D à 128D en utilisant le modèle GraphSAGE.
        
        Args:
            embedding: Embedding de 1024D
            
        Returns:
            Embedding projeté de 128D
        """
        if not self.load_model():
            logger.error("Impossible de charger le modèle GraphSAGE")
            return None
        
        try:
            # Convertir l'embedding en tensor
            x = torch.tensor([embedding], dtype=torch.float)
            
            # Créer un graphe avec un seul nœud (pas d'arêtes)
            edge_index = torch.empty((2, 0), dtype=torch.long)
            data = Data(x=x, edge_index=edge_index)
            
            # Projeter l'embedding
            with torch.no_grad():
                projected_embedding = self.model(data.x, data.edge_index).squeeze(0).numpy()
            
            logger.info(f"Embedding projeté avec succès de {embedding.shape} à {projected_embedding.shape}")
            return projected_embedding
        except Exception as e:
            logger.error(f"Erreur lors de la projection de l'embedding: {str(e)}")
            return None

# Initialiser l'état du modèle GraphSAGE
graphsage_model_state = GraphSAGEModelState()

def format_user_profile_esco(db: Session, user_id: int) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Formate le profil utilisateur selon les différents styles ESCO.
    
    Args:
        db: Session de base de données
        user_id: ID de l'utilisateur
        
    Returns:
        Tuple contenant les profils formatés (occupation, skill, skillgroup, full) ou None en cas d'échec
    """
    try:
        # Vérifier si le module de formatage ESCO est disponible
        if esco_formatter is None:
            logger.error("Le module de formatage ESCO n'est pas disponible")
            logger.info("Assurez-vous que le module format_user_profile_esco_style.py est présent dans le répertoire 'scripts'")
            logger.info("Et que toutes les dépendances requises sont installées (langchain, langchain-openai, etc.)")
            return None, None, None, None
            
        # Récupérer les données utilisateur
        user_data = fetch_user_data(db, user_id)
        if not user_data:
            logger.error(f"Aucune donnée utilisateur trouvée pour l'utilisateur {user_id}")
            return None, None, None, None
            
        # Extraire les données nécessaires pour le formatage ESCO
        profile = user_data.get("profile", {})
        skills = user_data.get("skills", {})
        riasec = user_data.get("riasec", {})
        
        # Vérifier que les fonctions de formatage ESCO existent
        if not hasattr(esco_formatter, "format_esco_occupation") or \
           not hasattr(esco_formatter, "format_esco_skill") or \
           not hasattr(esco_formatter, "format_esco_skillgroup") or \
           not hasattr(esco_formatter, "format_esco_full_profile"):
            logger.error("Les fonctions de formatage ESCO n'existent pas dans le module ESCO")
            return None, None, None, None
        
        # Formater le profil d'occupation ESCO
        occupation_profile = esco_formatter.format_esco_occupation(profile, skills, riasec)
        if occupation_profile is None:
            logger.error("Le formatage du profil d'occupation ESCO a échoué")
            return None, None, None, None
        
        # Formater les compétences individuelles ESCO
        skill_profiles = []
        for skill_name, skill_score in list(skills.items())[:5]:  # Limiter à 5 compétences
            formatted_skill = esco_formatter.format_esco_skill(skill_name, skill_score, profile)
            if formatted_skill:
                skill_profiles.append(formatted_skill)
        
        if not skill_profiles:
            logger.error("Le formatage des compétences ESCO a échoué")
            return occupation_profile, None, None, None
        
        skill_profile = "\n".join(skill_profiles)
        
        # Formater le groupe de compétences ESCO
        group_label = "Compétences techniques"
        skill_names = ["problem_solving", "analytical_thinking", "critical_thinking"]
        skillgroup_profile = esco_formatter.format_esco_skillgroup(group_label, skill_names, profile, riasec)
        if skillgroup_profile is None:
            logger.error("Le formatage du groupe de compétences ESCO a échoué")
            return occupation_profile, skill_profile, None, None
        
        # Formater le profil complet ESCO
        full_profile = esco_formatter.format_esco_full_profile(occupation_profile, skillgroup_profile, skill_profiles, profile, riasec)
        if full_profile is None:
            logger.error("Le formatage du profil complet ESCO a échoué")
            return occupation_profile, skill_profile, skillgroup_profile, None
        
        logger.info(f"Profils ESCO formatés avec succès pour l'utilisateur {user_id}")
        return occupation_profile, skill_profile, skillgroup_profile, full_profile
        
    except Exception as e:
        logger.error(f"Erreur lors du formatage des profils ESCO: {str(e)}")
        return None, None, None, None

def generate_esco_embeddings(db: Session, user_id: int) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Génère des embeddings à partir des profils ESCO formatés.
    
    Args:
        db: Session de base de données
        user_id: ID de l'utilisateur
        
    Returns:
        Tuple contenant les embeddings (occupation, skill, skillgroup, full) ou None en cas d'échec
    """
    try:
        # Formater les profils ESCO
        occupation_profile, skill_profile, skillgroup_profile, full_profile = format_user_profile_esco(db, user_id)
        
        # Stocker les profils ESCO formatés dans la base de données
        try:
            update_parts = []
            params = {"user_id": user_id}
            
            if occupation_profile:
                update_parts.append("esco_occupation_profile = :occupation_profile")
                params["occupation_profile"] = occupation_profile
                
            if skill_profile:
                update_parts.append("esco_skill_profile = :skill_profile")
                params["skill_profile"] = skill_profile
                
            if skillgroup_profile:
                update_parts.append("esco_skillsgroup_profile = :skillsgroup_profile")
                params["skillsgroup_profile"] = skillgroup_profile
                
            if full_profile:
                update_parts.append("esco_full_profile = :full_profile")
                params["full_profile"] = full_profile
            
            if update_parts:
                update_query = text(f"""
                    UPDATE user_profiles
                    SET {', '.join(update_parts)}
                    WHERE user_id = :user_id
                """)
                db.execute(update_query, params)
                db.commit()
                logger.info(f"Profils ESCO stockés avec succès pour l'utilisateur {user_id}")
        except Exception as e:
            logger.error(f"Erreur lors du stockage des profils ESCO: {str(e)}")
            db.rollback()
        
        # Générer les embeddings
        occupation_embedding = None
        skill_embedding = None
        skillgroup_embedding = None
        full_embedding = None
        
        if occupation_profile:
            occupation_embedding = generate_embedding_from_text_384(text=occupation_profile)
            logger.info(f"Embedding d'occupation ESCO généré avec succès: {occupation_embedding.shape if occupation_embedding is not None else None}")

        if skill_profile:
            skill_embedding = generate_embedding_from_text_384(text=skill_profile)
            logger.info(f"Embedding de compétence ESCO généré avec succès: {skill_embedding.shape if skill_embedding is not None else None}")

        if skillgroup_profile:
            skillgroup_embedding = generate_embedding_from_text_384(text=skillgroup_profile)
            logger.info(f"Embedding de groupe de compétences ESCO généré avec succès: {skillgroup_embedding.shape if skillgroup_embedding is not None else None}")

        if full_profile:
            full_embedding = generate_embedding_from_text_384(text=full_profile)
            logger.info(f"Embedding complet ESCO généré avec succès: {full_embedding.shape if full_embedding is not None else None}")

        return occupation_embedding, skill_embedding, skillgroup_embedding, full_embedding
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des embeddings ESCO: {str(e)}")
        return None, None, None, None

def store_direct_esco_embeddings(db: Session, user_id: int, embeddings: Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]) -> bool:
    """
    Store 384-dimensional embeddings directly in the database without GraphSAGE projection.
    
    Args:
        db: Database session
        user_id: User ID
        embeddings: Tuple of embeddings (occupation, skill, skillgroup, full)
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        occupation_embedding, skill_embedding, skillgroup_embedding, full_embedding = embeddings

        success = True
        if occupation_embedding is not None:
            # Convert to list if it's a numpy array, otherwise use as is
            embedding_list = occupation_embedding.tolist() if isinstance(occupation_embedding, np.ndarray) else occupation_embedding
            success &= store_embedding(db, user_id, embedding_list, column_name="esco_embedding_occupation")
            
        if skill_embedding is not None:
            embedding_list = skill_embedding.tolist() if isinstance(skill_embedding, np.ndarray) else skill_embedding
            success &= store_embedding(db, user_id, embedding_list, column_name="esco_embedding_skill")
            
        if skillgroup_embedding is not None:
            embedding_list = skillgroup_embedding.tolist() if isinstance(skillgroup_embedding, np.ndarray) else skillgroup_embedding
            success &= store_embedding(db, user_id, embedding_list, column_name="esco_embedding_skillsgroup")
            
        if full_embedding is not None:
            embedding_list = full_embedding.tolist() if isinstance(full_embedding, np.ndarray) else full_embedding
            success &= store_embedding(db, user_id, embedding_list, column_name="esco_embedding")

        if success:
            logger.info(f"✅ All 384D embeddings stored successfully for user {user_id}")
        else:
            logger.error(f"❌ One or more embeddings failed to store for user {user_id}")

        return success
    except Exception as e:
        logger.error(f"❌ Error storing direct embeddings: {str(e)}")
        return False

def process_user_esco_embeddings(db: Session, user_id: int) -> bool:
    """
    Process ESCO embeddings for a user - generate and store 384D embeddings directly.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        # Generate ESCO embeddings
        embeddings = generate_esco_embeddings(db, user_id)
        if all(e is None for e in embeddings):
            logger.error(f"❌ Failed to generate ESCO embeddings for user {user_id}")
            return False

        # Store embeddings directly without projection
        success = store_direct_esco_embeddings(db, user_id, embeddings)
        if success:
            logger.info(f"✅ ESCO embeddings processed successfully for user {user_id}")
        else:
            logger.error(f"❌ Failed to process ESCO embeddings for user {user_id}")
        
        return success
    except Exception as e:
        logger.error(f"❌ Error in process_user_esco_embeddings: {str(e)}")
        return False