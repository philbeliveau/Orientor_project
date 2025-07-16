"""
Service de visualisation du graphe d'arbre de compétences.

Ce service permet de visualiser le graphe résultant de la traversée
en utilisant différentes bibliothèques de visualisation.
"""

import os
import logging
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import json
from pathlib import Path
import base64
from io import BytesIO

# Configuration du logger
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SkillTreeVisualization:
    """
    Service pour visualiser le graphe d'arbre de compétences.
    
    Ce service propose différentes méthodes de visualisation du graphe
    résultant de la traversée, adaptées à différents contextes d'utilisation.
    """
    
    def __init__(self):
        """
        Initialise le service de visualisation.
        """
        # Définir les couleurs par type de nœud
        self.node_colors = {
            "occupation": "#4285F4",  # Bleu
            "skill": "#34A853",       # Vert
            "skillgroup": "#FBBC05",  # Jaune
            "unknown": "#EA4335"      # Rouge
        }
        
        # Définir les tailles par type de nœud
        self.node_sizes = {
            "occupation": 20,
            "skill": 15,
            "skillgroup": 18,
            "unknown": 10
        }
        
        logger.info("Service de visualisation initialisé")
    
    def _create_networkx_graph(self, graph_data: Dict[str, Any]) -> nx.Graph:
        """
        Crée un graphe NetworkX à partir des données du graphe.
        
        Args:
            graph_data: Données du graphe (nœuds et arêtes)
        
        Returns:
            Graphe NetworkX
        """
        G = nx.Graph()
        
        # Ajouter les nœuds
        for node_id, node_data in graph_data.get("nodes", {}).items():
            G.add_node(
                node_id,
                label=node_data.get("preferredlabel", node_data.get("label", "")),
                type=node_data.get("type", "unknown"),
                is_anchor=node_data.get("is_anchor", False),
                depth=node_data.get("depth", 0)
            )
        
        # Ajouter les arêtes
        for edge in graph_data.get("edges", []):
            source = edge.get("source")
            target = edge.get("target")
            weight = edge.get("weight", 1.0)
            
            if source and target:
                G.add_edge(source, target, weight=weight)
        
        return G
    
    def visualize_matplotlib(self, 
                           graph_data: Dict[str, Any], 
                           output_path: Optional[str] = None,
                           title: str = "Arbre de compétences",
                           figsize: Tuple[int, int] = (12, 10)) -> Optional[str]:
        """
        Visualise le graphe avec Matplotlib.
        
        Args:
            graph_data: Données du graphe (nœuds et arêtes)
            output_path: Chemin de sortie pour enregistrer l'image (si None, retourne l'image encodée en base64)
            title: Titre du graphique
            figsize: Taille de la figure (largeur, hauteur)
        
        Returns:
            Chemin de l'image enregistrée ou image encodée en base64 (si output_path est None)
        """
        try:
            # Créer le graphe NetworkX
            G = self._create_networkx_graph(graph_data)
            
            if len(G.nodes) == 0:
                logger.warning("Le graphe ne contient aucun nœud")
                return None
            
            # Créer la figure
            plt.figure(figsize=figsize)
            plt.title(title)
            
            # Calculer la disposition du graphe
            pos = nx.spring_layout(G, seed=42)
            
            # Préparer les couleurs et tailles des nœuds
            node_colors = [self.node_colors.get(G.nodes[node]["type"], self.node_colors["unknown"]) for node in G.nodes]
            node_sizes = [self.node_sizes.get(G.nodes[node]["type"], self.node_sizes["unknown"]) * 20 for node in G.nodes]
            
            # Identifier les nœuds d'ancrage
            anchor_nodes = [node for node in G.nodes if G.nodes[node].get("is_anchor", False)]
            
            # Dessiner le graphe
            nx.draw_networkx_edges(G, pos, alpha=0.3, width=1)
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
            
            # Mettre en évidence les nœuds d'ancrage
            if anchor_nodes:
                nx.draw_networkx_nodes(
                    G, pos, 
                    nodelist=anchor_nodes, 
                    node_color=[self.node_colors.get(G.nodes[node]["type"], self.node_colors["unknown"]) for node in anchor_nodes],
                    node_size=[self.node_sizes.get(G.nodes[node]["type"], self.node_sizes["unknown"]) * 30 for node in anchor_nodes],
                    edgecolors="black",
                    linewidths=2
                )
            
            # Ajouter les étiquettes des nœuds avec un fond blanc pour une meilleure lisibilité
            labels = {node: G.nodes[node]["label"] for node in G.nodes}
            nx.draw_networkx_labels(
                G, pos,
                labels=labels,
                font_size=10,
                font_family="sans-serif",
                font_weight="bold",
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", boxstyle="round,pad=0.3")
            )
            
            # Ajouter une légende
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=node_type)
                for node_type, color in self.node_colors.items()
            ]
            plt.legend(handles=legend_elements, loc="upper right")
            
            plt.axis("off")
            
            # Enregistrer ou retourner l'image
            if output_path:
                plt.savefig(output_path, bbox_inches="tight", dpi=300)
                plt.close()
                logger.info(f"Graphe enregistré dans {output_path}")
                return output_path
            else:
                # Encoder l'image en base64
                buf = BytesIO()
                plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
                plt.close()
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode("utf-8")
                logger.info("Graphe encodé en base64")
                return img_str
                
        except Exception as e:
            logger.error(f"Erreur lors de la visualisation avec Matplotlib: {str(e)}")
            return None
    
    def visualize_plotly(self, 
                       graph_data: Dict[str, Any],
                       output_path: Optional[str] = None,
                       title: str = "Arbre de compétences") -> Optional[Dict[str, Any]]:
        """
        Visualise le graphe avec Plotly pour une visualisation interactive.
        
        Args:
            graph_data: Données du graphe (nœuds et arêtes)
            output_path: Chemin de sortie pour enregistrer le HTML (si None, retourne la figure Plotly)
            title: Titre du graphique
        
        Returns:
            Figure Plotly ou None en cas d'échec
        """
        try:
            # Créer le graphe NetworkX
            G = self._create_networkx_graph(graph_data)
            
            if len(G.nodes) == 0:
                logger.warning("Le graphe ne contient aucun nœud")
                return None
            
            # Calculer la disposition du graphe
            pos = nx.spring_layout(G, seed=42)
            
            # Préparer les données des nœuds
            node_x = []
            node_y = []
            node_hover_text = []
            node_text = []  # Pour les étiquettes visibles
            node_color = []
            node_size = []
            
            for node in G.nodes:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # Texte du nœud
                label = G.nodes[node].get("preferredlabel", G.nodes[node].get("label", ""))
                node_type = G.nodes[node].get("type", "unknown")
                is_anchor = G.nodes[node].get("is_anchor", False)
                depth = G.nodes[node].get("depth", 0)
                
                # Texte de survol détaillé
                node_hover_text.append(f"ID: {node}<br>Label: {label}<br>Type: {node_type}<br>Depth: {depth}")
                
                # Étiquette visible sur le graphe
                node_text.append(label)
                
                # Couleur et taille du nœud
                node_color.append(self.node_colors.get(node_type, self.node_colors["unknown"]))
                size = self.node_sizes.get(node_type, self.node_sizes["unknown"])
                if is_anchor:
                    size *= 1.5
                node_size.append(size)
            
            # Créer le tracé des nœuds
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                hovertext=node_hover_text,
                text=node_text,
                textposition="top center",
                textfont=dict(size=10, color='black', family='Arial, sans-serif'),
                marker=dict(
                    color=node_color,
                    size=node_size,
                    line=dict(width=1, color='#888'),
                    opacity=0.8
                )
            )
            
            # Préparer les données des arêtes
            edge_x = []
            edge_y = []
            edge_text = []
            
            for edge in G.edges:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
                weight = G.edges[edge].get("weight", 1.0)
                edge_text.append(f"Weight: {weight:.2f}")
            
            # Créer le tracé des arêtes
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Créer la figure
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title=title,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
            )
            
            # Ajouter une légende
            for node_type, color in self.node_colors.items():
                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=10, color=color),
                    name=node_type,
                    showlegend=True
                ))
            
            # Enregistrer ou retourner la figure
            if output_path:
                fig.write_html(output_path)
                logger.info(f"Graphe interactif enregistré dans {output_path}")
                return {"path": output_path}
            else:
                logger.info("Figure Plotly créée")
                return {"figure": fig}
                
        except Exception as e:
            logger.error(f"Erreur lors de la visualisation avec Plotly: {str(e)}")
            return None
    
    def export_graph_json(self, 
                        graph_data: Dict[str, Any],
                        output_path: str) -> bool:
        """
        Exporte le graphe au format JSON.
        
        Args:
            graph_data: Données du graphe (nœuds et arêtes)
            output_path: Chemin de sortie pour enregistrer le JSON
        
        Returns:
            Booléen indiquant le succès ou l'échec
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(graph_data, f, indent=2)
            
            logger.info(f"Graphe exporté au format JSON dans {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exportation du graphe au format JSON: {str(e)}")
            return False
    
    def create_streamlit_visualization(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée une visualisation adaptée à Streamlit.
        
        Cette méthode retourne les données nécessaires pour créer une visualisation
        dans une application Streamlit.
        
        Args:
            graph_data: Données du graphe (nœuds et arêtes)
        
        Returns:
            Dictionnaire contenant les données pour la visualisation Streamlit
        """
        try:
            # Créer le graphe NetworkX
            G = self._create_networkx_graph(graph_data)
            
            if len(G.nodes) == 0:
                logger.warning("Le graphe ne contient aucun nœud")
                return {"error": "Le graphe ne contient aucun nœud"}
            
            # Calculer la disposition du graphe
            pos = nx.spring_layout(G, seed=42)
            
            # Préparer les données des nœuds
            nodes_data = []
            for node_id, node_data in graph_data.get("nodes", {}).items():
                x, y = pos[node_id]
                
                node_type = node_data.get("type", "unknown")
                is_anchor = node_data.get("is_anchor", False)
                
                nodes_data.append({
                    "id": node_id,
                    "label": node_data.get("preferredlabel", node_data.get("label", "")),
                    "type": node_type,
                    "is_anchor": is_anchor,
                    "depth": node_data.get("depth", 0),
                    "x": float(x),
                    "y": float(y),
                    "color": self.node_colors.get(node_type, self.node_colors["unknown"]),
                    "size": self.node_sizes.get(node_type, self.node_sizes["unknown"]) * (1.5 if is_anchor else 1.0),
                    "show_label": True  # Toujours afficher les étiquettes
                })
            
            # Préparer les données des arêtes
            edges_data = []
            for edge in graph_data.get("edges", []):
                source = edge.get("source")
                target = edge.get("target")
                weight = edge.get("weight", 1.0)
                
                if source and target:
                    edges_data.append({
                        "source": source,
                        "target": target,
                        "weight": weight
                    })
            
            # Créer les données pour la visualisation Streamlit
            visualization_data = {
                "nodes": nodes_data,
                "edges": edges_data,
                "node_types": list(self.node_colors.keys()),
                "node_colors": self.node_colors
            }
            
            # Créer également une image statique pour l'aperçu
            img_base64 = self.visualize_matplotlib(graph_data)
            if img_base64:
                visualization_data["preview_image"] = img_base64
            
            logger.info("Données de visualisation Streamlit créées")
            return visualization_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la visualisation Streamlit: {str(e)}")
            return {"error": str(e)}