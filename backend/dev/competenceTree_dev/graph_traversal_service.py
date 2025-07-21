"""
Service de traversée du graphe ESCO en utilisant GraphSAGE.

Ce service permet de traverser le graphe ESCO à partir de nœuds d'ancrage
en utilisant le modèle GraphSAGE pour calculer les similarités entre les nœuds.
"""

import os
import logging
import torch
import numpy as np
import networkx as nx
from typing import List, Dict, Any, Optional, Tuple, Set
from pathlib import Path
import json
import pickle
from collections import defaultdict, deque
import sys

# Configuration du logger early
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Production-grade path resolution for Railway deployment compatibility
def get_production_paths():
    """Get correct paths for both local development and Railway deployment."""
    current_file = os.path.abspath(__file__)
    
    # Try Railway deployment paths first
    railway_paths = {
        'backend': '/app',
        'services': '/app/app/services', 
        'gnn': '/app/app/services/GNN',
        'model': '/app/app/services/GNN/best_model_20250520_022237.pt',
        'data_dir': '/app/app/data'  # Moved from /app/dev which might not deploy
    }
    
    # Check if we're in Railway environment
    if os.path.exists('/app/main_deploy.py'):
        return railway_paths
    
    # Local development paths
    local_backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_paths = {
        'backend': local_backend,
        'services': os.path.join(local_backend, "app", "services"),
        'gnn': os.path.join(local_backend, "app", "services", "GNN"),
        'model': os.path.join(local_backend, "app", "services", "GNN", "best_model_20250520_022237.pt")
    }
    
    return local_paths

# Get production paths
paths = get_production_paths()
backend_path = paths['backend']
services_path = paths['services'] 
gnn_path = paths['gnn']

# Add both paths to ensure imports work
if services_path not in sys.path:
    sys.path.insert(0, services_path)
if gnn_path not in sys.path:
    sys.path.insert(0, gnn_path)

try:
    from GraphSage import GraphSAGE, CareerTreeModel
    logger.info("GraphSAGE imported successfully from GNN directory")
except ImportError as e:
    logger.warning(f"Direct import failed: {e}, trying fallback method")
    try:
        # Fallback import method
        from GNN.GraphSage import GraphSAGE, CareerTreeModel
        logger.info("GraphSAGE imported successfully using fallback method")
    except ImportError as e:
        logger.error(f"All import methods failed: {e}")
        # Define dummy classes to prevent total failure
        class GraphSAGE:
            pass
        class CareerTreeModel:
            def __init__(self, *args, **kwargs):
                pass
            def eval(self):
                pass
            def load_state_dict(self, *args, **kwargs):
                pass


class GraphTraversalService:
    """
    Service pour traverser le graphe ESCO en utilisant GraphSAGE.
    
    Ce service utilise le modèle GraphSAGE pour calculer les similarités entre les nœuds
    et traverser le graphe à partir de nœuds d'ancrage.
    """
    
    def __init__(self, 
                model_path: Optional[str] = None,
                graph_data_path: Optional[str] = None,
                node_metadata_path: Optional[str] = None,
                max_depth: int = 10):
        """
        Initialise le service de traversée du graphe.
        
        Args:
            model_path: Chemin vers le modèle GraphSAGE préentraîné
            graph_data_path: Chemin vers les données du graphe ESCO
            node_metadata_path: Chemin vers les métadonnées des nœuds
            max_depth: Profondeur maximale de traversée
        """
        # Production-grade model path resolution  
        if model_path is None:
            # Use the production path system
            paths = get_production_paths()
            model_path = paths['model']
            logger.info(f"Using model path: {model_path}")
        
        # Chemin par défaut vers le dossier de données
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        
        # Chemins vers les fichiers de données
        self.idx2node_path = os.path.join(data_dir, "idx2node.json")
        self.node2idx_path = os.path.join(data_dir, "node2idx.json")
        self.node_metadata_path = os.path.join(data_dir, "node_metadata.json")
        self.edge_type_dict_path = os.path.join(data_dir, "edge_type_dict.json")
        self.edge_index_path = os.path.join(data_dir, "edge_index.pt")
        self.node_features_path = os.path.join(data_dir, "node_features.pt")
        self.edge_type_path = os.path.join(data_dir, "edge_type.json")
        self.edge_type_indices_path = os.path.join(data_dir, "edge_type_indices.json")
        
        self.model_path = model_path
        # Ne pas écraser les chemins déjà définis si les paramètres sont None
        if graph_data_path is not None:
            self.graph_data_path = graph_data_path
        if node_metadata_path is not None:
            self.node_metadata_path = node_metadata_path
        self.max_depth = max_depth
        
        # Charger le modèle GraphSAGE
        self.model = self._load_model()
        
        # Initialiser les structures de données
        self.idx2node = {}
        self.node2idx = {}
        self.node_metadata = {}
        self.edge_type_dict = {}
        self.edge_type = {}
        self.edge_type_indices = {}
        
        # Charger les données du graphe
        self._load_graph_data()
        
        # Créer le graphe NetworkX à partir des données chargées
        self.graph = self._create_networkx_graph()
        
        logger.info(f"Service de traversée du graphe initialisé avec {len(self.graph.nodes)} nœuds et {len(self.graph.edges)} arêtes")
    
    def _load_model(self) -> Optional[CareerTreeModel]:
        """
        Charge le modèle GraphSAGE préentraîné.
        
        Returns:
            Le modèle GraphSAGE chargé ou None en cas d'échec
        """
        try:
            # Vérifier si le fichier du modèle existe
            if not os.path.exists(self.model_path):
                logger.error(f"Le fichier du modèle n'existe pas: {self.model_path}")
                return None
            
            # Charger le checkpoint
            checkpoint = torch.load(self.model_path, map_location="cpu", weights_only=False)
            
            # Instancier le modèle
            model = CareerTreeModel(
                input_dim=384,  # Dimension des embeddings
                hidden_dim=128,
                output_dim=128,
                dropout=0.2
            )
            
            # Charger les poids du modèle
            if "model_state_dict" not in checkpoint:
                logger.error("Le checkpoint ne contient pas 'model_state_dict'")
                return None
            
            model.load_state_dict(checkpoint["model_state_dict"])
            model.eval()  # Mettre le modèle en mode évaluation
            
            logger.info("Modèle GraphSAGE chargé avec succès")
            return model
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {str(e)}")
            return None
    
    def _load_graph_data(self) -> bool:
        """
        Charge les données du graphe à partir des fichiers dans le dossier data/.
        
        Returns:
            Booléen indiquant le succès ou l'échec du chargement
        """
        try:
            # Charger les mappages d'index
            if os.path.exists(self.idx2node_path):
                with open(self.idx2node_path, 'r') as f:
                    self.idx2node = json.load(f)
                logger.info(f"Mappages idx2node chargés pour {len(self.idx2node)} nœuds")
            else:
                logger.warning(f"Le fichier idx2node n'existe pas: {self.idx2node_path}")
            
            if os.path.exists(self.node2idx_path):
                with open(self.node2idx_path, 'r') as f:
                    self.node2idx = json.load(f)
                logger.info(f"Mappages node2idx chargés pour {len(self.node2idx)} nœuds")
            else:
                logger.warning(f"Le fichier node2idx n'existe pas: {self.node2idx_path}")
            
            # Charger les métadonnées des nœuds
            if os.path.exists(self.node_metadata_path):
                with open(self.node_metadata_path, 'r') as f:
                    self.node_metadata = json.load(f)
                logger.info(f"Métadonnées chargées pour {len(self.node_metadata)} nœuds")
            else:
                logger.warning(f"Le fichier des métadonnées n'existe pas: {self.node_metadata_path}")
            
            # Charger le dictionnaire des types d'arêtes
            if os.path.exists(self.edge_type_dict_path):
                with open(self.edge_type_dict_path, 'r') as f:
                    self.edge_type_dict = json.load(f)
                logger.info(f"Dictionnaire des types d'arêtes chargé avec {len(self.edge_type_dict)} types")
            else:
                logger.warning(f"Le fichier du dictionnaire des types d'arêtes n'existe pas: {self.edge_type_dict_path}")
            
            # Charger les index d'arêtes
            if os.path.exists(self.edge_index_path):
                self.edge_index = torch.load(self.edge_index_path)
                logger.info(f"Index d'arêtes chargés avec forme {self.edge_index.shape}")
            else:
                logger.warning(f"Le fichier des index d'arêtes n'existe pas: {self.edge_index_path}")
                self.edge_index = torch.empty((2, 0), dtype=torch.long)
            
            # Charger les caractéristiques des nœuds
            if os.path.exists(self.node_features_path):
                self.node_features_tensor = torch.load(self.node_features_path)
                logger.info(f"Caractéristiques des nœuds chargées avec forme {self.node_features_tensor.shape}")
            else:
                logger.warning(f"Le fichier des caractéristiques des nœuds n'existe pas: {self.node_features_path}")
                self.node_features_tensor = torch.empty((0, 384), dtype=torch.float)
            
            # Charger les informations sur les types d'arêtes (optionnel)
            if os.path.exists(self.edge_type_path):
                with open(self.edge_type_path, 'r') as f:
                    self.edge_type = json.load(f)
                logger.info(f"Types d'arêtes chargés")
            else:
                logger.warning(f"Le fichier des types d'arêtes n'existe pas: {self.edge_type_path}")
            
            if os.path.exists(self.edge_type_indices_path):
                with open(self.edge_type_indices_path, 'r') as f:
                    self.edge_type_indices = json.load(f)
                logger.info(f"Indices des types d'arêtes chargés")
            else:
                logger.warning(f"Le fichier des indices des types d'arêtes n'existe pas: {self.edge_type_indices_path}")
            
            # Convertir les caractéristiques des nœuds en dictionnaire pour une utilisation plus facile
            self.node_features = {}
            if hasattr(self, 'node_features_tensor') and self.node_features_tensor.shape[0] > 0:
                for idx, node_id in self.idx2node.items():
                    idx = int(idx)
                    if idx < self.node_features_tensor.shape[0]:
                        self.node_features[node_id] = self.node_features_tensor[idx].numpy()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données du graphe: {str(e)}")
            return False
    
    def _create_networkx_graph(self) -> nx.Graph:
        """
        Crée un graphe NetworkX à partir des données chargées ou charge un graphe prétraité.
        
        Returns:
            Graphe NetworkX
        """
        try:
            # Chemin vers le graphe prétraité
            networkx_graph_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data",
                "networkx_graph.pkl"
            )
            
            # Vérifier si le graphe prétraité existe
            if os.path.exists(networkx_graph_path):
                logger.info(f"Chargement du graphe prétraité depuis {networkx_graph_path}...")
                with open(networkx_graph_path, 'rb') as f:
                    G = pickle.load(f)
                logger.info(f"Graphe NetworkX chargé avec {len(G.nodes)} nœuds et {len(G.edges)} arêtes")
                return G
            
            logger.info("Graphe prétraité non trouvé, création d'un nouveau graphe...")
            
            # Créer le graphe
            G = nx.Graph()
            
            # Ajouter les nœuds avec leurs métadonnées
            for node_id, metadata in self.node_metadata.items():
                G.add_node(node_id, **metadata)
            
            # Ajouter les arêtes si edge_index existe
            if hasattr(self, 'edge_index') and self.edge_index.shape[1] > 0:
                for i in range(self.edge_index.shape[1]):
                    src_idx = self.edge_index[0, i].item()
                    tgt_idx = self.edge_index[1, i].item()
                    
                    # Convertir les indices en IDs de nœuds
                    src_id = self.idx2node.get(str(src_idx))
                    tgt_id = self.idx2node.get(str(tgt_idx))
                    
                    if src_id and tgt_id:
                        # Déterminer le type d'arête si disponible
                        edge_type = "default"
                        if hasattr(self, 'edge_type_indices') and str(i) in self.edge_type_indices:
                            type_idx = self.edge_type_indices[str(i)]
                            edge_type = self.edge_type.get(str(type_idx), "default")
                        
                        # Ajouter l'arête avec un poids par défaut de 1.0
                        G.add_edge(src_id, tgt_id, weight=1.0, type=edge_type)
            
            logger.info(f"Graphe NetworkX créé avec {len(G.nodes)} nœuds et {len(G.edges)} arêtes")
            return G
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphe NetworkX: {str(e)}")
            return nx.Graph()
    
    def compute_node_similarity(self, node1_id: str, node2_id: str) -> float:
        """
        Calcule la similarité entre deux nœuds en utilisant GraphSAGE.
        
        Args:
            node1_id: ID du premier nœud
            node2_id: ID du deuxième nœud
        
        Returns:
            Score de similarité entre 0 et 1
        """
        # Vérifier si les nœuds existent dans le graphe
        if node1_id not in self.node_features or node2_id not in self.node_features:
            logger.warning(f"Un des nœuds n'existe pas dans le graphe: {node1_id}, {node2_id}")
            return 0.0
        
        try:
            # Récupérer les caractéristiques des nœuds
            node1_features = self.node_features[node1_id]
            node2_features = self.node_features[node2_id]
            
            # Convertir en tensors PyTorch
            node1_tensor = torch.tensor(node1_features, dtype=torch.float32).unsqueeze(0)
            node2_tensor = torch.tensor(node2_features, dtype=torch.float32).unsqueeze(0)
            
            # Si le modèle GraphSAGE est disponible, l'utiliser pour calculer la similarité
            if self.model is not None:
                # Créer un mini-graphe pour les deux nœuds
                x = torch.cat([node1_tensor, node2_tensor], dim=0)
                edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
                
                # Calculer les embeddings avec GraphSAGE
                with torch.no_grad():
                    node_embeddings = self.model.encoder(x, edge_index)
                
                # Calculer la similarité cosinus
                node1_embedding = node_embeddings[0]
                node2_embedding = node_embeddings[1]
                
                similarity = torch.cosine_similarity(node1_embedding, node2_embedding, dim=0).item()
            else:
                # Fallback: calculer directement la similarité cosinus entre les caractéristiques
                similarity = torch.cosine_similarity(node1_tensor, node2_tensor, dim=1).item()
            
            # Normaliser entre 0 et 1
            similarity = (similarity + 1) / 2
            
            return similarity
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la similarité: {str(e)}")
            return 0.0
    
    def traverse_graph(self, 
                      anchor_node_ids: List[str], 
                      max_depth: Optional[int] = None,
                      min_similarity: float = 0.3,
                      max_nodes_per_level: int = 5) -> Dict[str, Any]:
        """
        Traverse le graphe à partir des nœuds d'ancrage.
        
        Args:
            anchor_node_ids: Liste des IDs des nœuds d'ancrage
            max_depth: Profondeur maximale de traversée (si None, utilise self.max_depth)
            min_similarity: Similarité minimale pour inclure un nœud
            max_nodes_per_level: Nombre maximum de nœuds à explorer par niveau
        
        Returns:
            Dictionnaire contenant le graphe résultant et les métadonnées
        """
        if max_depth is None:
            max_depth = self.max_depth
        
        # Vérifier si les nœuds d'ancrage existent dans le graphe
        valid_anchors = [node_id for node_id in anchor_node_ids if node_id in self.graph.nodes]
        if not valid_anchors:
            logger.warning("Aucun nœud d'ancrage valide")
            return {"nodes": {}, "edges": []}
        
        # Initialiser le graphe résultant
        result_graph = {
            "nodes": {},
            "edges": []
        }
        
        # Ensemble des nœuds visités
        visited = set()
        
        # File d'attente pour la traversée en largeur (BFS)
        queue = deque([(node_id, 0) for node_id in valid_anchors])  # (node_id, depth)
        
        # Ajouter les nœuds d'ancrage au graphe résultant
        for node_id in valid_anchors:
            node_metadata = self.node_metadata.get(node_id, {})
            node_type = node_metadata.get("type", "unknown")
            node_label = node_metadata.get("preferredlabel", node_metadata.get("label", ""))
            
            result_graph["nodes"][node_id] = {
                "id": node_id,
                "type": node_type,
                "label": node_label,
                "metadata": node_metadata,
                "is_anchor": True,
                "depth": 0
            }
            
            visited.add(node_id)
        
        # Traverser le graphe en largeur (BFS)
        while queue and len(result_graph["nodes"]) < 100:  # Limite de sécurité
            node_id, depth = queue.popleft()
            
            # Arrêter si la profondeur maximale est atteinte
            if depth >= max_depth:
                continue
            
            # Récupérer les voisins du nœud
            neighbors = list(self.graph.neighbors(node_id))
            
            # Calculer la similarité avec le nœud courant pour chaque voisin
            neighbor_similarities = []
            for neighbor_id in neighbors:
                if neighbor_id not in visited:
                    similarity = self.compute_node_similarity(node_id, neighbor_id)
                    if similarity >= min_similarity:
                        neighbor_similarities.append((neighbor_id, similarity))
            
            # Trier les voisins par similarité décroissante
            neighbor_similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Limiter le nombre de voisins par niveau
            neighbor_similarities = neighbor_similarities[:max_nodes_per_level]
            
            # Ajouter les voisins au graphe résultant
            for neighbor_id, similarity in neighbor_similarities:
                if neighbor_id not in visited:
                    # Ajouter le nœud
                    node_metadata = self.node_metadata.get(neighbor_id, {})
                    node_type = node_metadata.get("type", "unknown")
                    node_label = node_metadata.get("preferredlabel", node_metadata.get("label", ""))
                    
                    result_graph["nodes"][neighbor_id] = {
                        "id": neighbor_id,
                        "type": node_type,
                        "label": node_label,
                        "metadata": node_metadata,
                        "is_anchor": False,
                        "depth": depth + 1
                    }
                    
                    # Ajouter l'arête
                    result_graph["edges"].append({
                        "source": node_id,
                        "target": neighbor_id,
                        "weight": similarity,
                        "type": "similarity"
                    })
                    
                    # Marquer le nœud comme visité
                    visited.add(neighbor_id)
                    
                    # Ajouter le nœud à la file d'attente pour la prochaine itération
                    queue.append((neighbor_id, depth + 1))
        
        logger.info(f"Graphe traversé avec {len(result_graph['nodes'])} nœuds et {len(result_graph['edges'])} arêtes")
        return result_graph
    
    def get_node_info(self, node_id: str) -> Dict[str, Any]:
        """
        Récupère les informations d'un nœud.
        
        Args:
            node_id: ID du nœud
        
        Returns:
            Dictionnaire contenant les informations du nœud
        """
        if node_id not in self.graph.nodes:
            logger.warning(f"Le nœud n'existe pas dans le graphe: {node_id}")
            return {}
        
        node_metadata = self.node_metadata.get(node_id, {})
        node_data = self.graph.nodes[node_id]
        
        return {
            "id": node_id,
            "type": node_metadata.get("type", "unknown"),
            "label": node_metadata.get("preferredlabel", node_metadata.get("label", "")),
            "metadata": {**node_metadata, **node_data}
        }