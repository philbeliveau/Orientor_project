"""
Application Streamlit pour la traversée d'arbre de compétences.

Cette application permet de visualiser et d'explorer l'arbre de compétences
en utilisant GraphSAGE pour la traversée du graphe ESCO.
"""

# 1. Import Streamlit first and set page config
import streamlit as st
st.set_page_config(
    page_title="Explorateur d'arbre de compétences ESCO",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Import compatibility fixes and apply them
from competenceTree_dev.utils.streamlit_compat import apply_compatibility_fixes, verify_torch_model

# Apply all compatibility fixes
if not apply_compatibility_fixes():
    st.error("Erreur lors de l'application des correctifs de compatibilité")

# 3. Import other dependencies
import os
import sys
import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import json
from typing import List, Dict, Any, Optional, Tuple
import base64
from io import BytesIO
from pathlib import Path
import matplotlib.pyplot as plt
import time

# Désactiver les avertissements de PyTorch
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Configuration pour éviter les problèmes avec asyncio
import nest_asyncio
try:
    nest_asyncio.apply()
except:
    pass

# Vérifier le modèle GraphSAGE
model_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app", "services", "GNN", "best_model_20250520_022237.pt"
)
if not verify_torch_model(model_path):
    st.error("Erreur lors de la vérification du modèle GraphSAGE")

# Vérifier si le graphe prétraité existe et le créer si nécessaire
networkx_graph_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "networkx_graph.pkl")
if not os.path.exists(networkx_graph_path):
    st.info("Le graphe prétraité n'existe pas. Création du graphe en cours...")
    
    # Importer le script de sauvegarde du graphe
    from save_networkx_graph import save_networkx_graph
    
    # Exécuter le script
    with st.spinner("Création et sauvegarde du graphe NetworkX en cours... Cela peut prendre plusieurs minutes."):
        success = save_networkx_graph()
        if success:
            st.success("Graphe NetworkX créé et sauvegardé avec succès!")
        else:
            st.error("Erreur lors de la création et de la sauvegarde du graphe NetworkX.")

# Ajouter le répertoire parent au chemin d'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les services
from competenceTree_dev.anchor_discovery_service import AnchorDiscoveryService
from competenceTree_dev.graph_traversal_service import GraphTraversalService
from competenceTree_dev.skill_tree_visualization import SkillTreeVisualization

# Configuration du logger
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fonction pour charger un embedding depuis un fichier
def load_embedding_from_file(file):
    try:
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        # Essayer de charger comme JSON
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return np.array(data, dtype=np.float32)
        except:
            pass
        
        # Essayer de charger comme texte brut (valeurs séparées par des virgules ou des espaces)
        try:
            values = [float(x) for x in content.replace(',', ' ').split()]
            return np.array(values, dtype=np.float32)
        except:
            pass
        
        st.error("Format d'embedding non reconnu. Veuillez fournir un fichier JSON ou texte avec des valeurs numériques.")
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'embedding: {str(e)}")
        return None

# Fonction pour générer un embedding aléatoire (pour les tests)
def generate_random_embedding(dim=384):
    embedding = np.random.randn(dim).astype(np.float32)
    # Normaliser l'embedding
    embedding = embedding / np.linalg.norm(embedding)
    return embedding

# Fonction pour initialiser les services
@st.cache_resource
def init_services(pinecone_api_key=None):
    try:
        # Initialiser le service de découverte des nœuds d'ancrage
        anchor_service = AnchorDiscoveryService(api_key=pinecone_api_key)
        
        # Initialiser le service de traversée du graphe
        graph_service = GraphTraversalService()
        
        # Initialiser le service de visualisation
        viz_service = SkillTreeVisualization()
        
        return {
            "anchor_service": anchor_service,
            "graph_service": graph_service,
            "viz_service": viz_service
        }
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation des services: {str(e)}")
        return None

# Fonction pour afficher le graphe avec Plotly
def display_plotly_graph(graph_data):
    # Créer un graphe NetworkX
    import networkx as nx
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
    
    # Définir les couleurs par type de nœud
    node_colors = {
        "occupation": "#4285F4",  # Bleu
        "skill": "#34A853",       # Vert
        "skillgroup": "#FBBC05",  # Jaune
        "unknown": "#EA4335"      # Rouge
    }
    
    # Définir les tailles par type de nœud
    node_sizes = {
        "occupation": 20,
        "skill": 15,
        "skillgroup": 18,
        "unknown": 10
    }
    
    # Calculer la disposition du graphe
    pos = nx.spring_layout(G, seed=42)
    
    # Préparer les données des nœuds
    node_x = []
    node_y = []
    node_text = []
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
        
        node_text.append(f"ID: {node}<br>Label: {label}<br>Type: {node_type}<br>Depth: {depth}")
        
        # Couleur et taille du nœud
        node_color.append(node_colors.get(node_type, node_colors["unknown"]))
        size = node_sizes.get(node_type, node_sizes["unknown"])
        if is_anchor:
            size *= 1.5
        node_size.append(size)
    
    # Créer le tracé des nœuds
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
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
    
    for edge in G.edges:
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
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
            title="Arbre de compétences",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )
    
    # Ajouter une légende
    for node_type, color in node_colors.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color),
            name=node_type,
            showlegend=True
        ))
    
    # Afficher la figure
    st.plotly_chart(fig, use_container_width=True)

# Fonction pour afficher les informations des nœuds
def display_nodes_info(graph_data):
    nodes = graph_data.get("nodes", {})
    if not nodes:
        st.info("Aucun nœud à afficher")
        return
    
    # Créer un DataFrame pour afficher les informations des nœuds
    nodes_info = []
    for node_id, node_data in nodes.items():
        nodes_info.append({
            "ID": node_id,
            "Label": node_data.get("preferredlabel", node_data.get("label", "")),
            "Type": node_data.get("type", "unknown"),
            "Ancrage": "Oui" if node_data.get("is_anchor", False) else "Non",
            "Profondeur": node_data.get("depth", 0)
        })
    
    # Trier par profondeur et type
    nodes_df = pd.DataFrame(nodes_info)
    nodes_df = nodes_df.sort_values(by=["Profondeur", "Type"])
    
    # Afficher le DataFrame
    st.dataframe(nodes_df, use_container_width=True)

# Fonction principale de l'application
def main():
    # Titre de l'application
    st.title("🌳 Explorateur d'arbre de compétences ESCO")
    st.markdown("""
    Cette application permet d'explorer l'arbre de compétences ESCO en utilisant GraphSAGE
    pour la traversée du graphe. Vous pouvez fournir un embedding ou en générer un aléatoire,
    puis explorer les compétences associées.
    """)
    
    # Barre latérale pour les paramètres
    st.sidebar.title("⚙️ Paramètres")
    
    # Clé API Pinecone
    pinecone_api_key = st.sidebar.text_input("Clé API Pinecone", 
                                            value=os.getenv("PINECONE_API_KEY", ""),
                                            type="password")
    
    # Initialiser les services
    services = init_services(pinecone_api_key)
    if not services:
        st.error("Impossible d'initialiser les services. Veuillez vérifier la clé API Pinecone.")
        return
    
    anchor_service = services["anchor_service"]
    graph_service = services["graph_service"]
    viz_service = services["viz_service"]
    
    # Paramètres de l'embedding
    st.sidebar.subheader("Embedding")
    embedding_source = st.sidebar.radio(
        "Source de l'embedding",
        ["Fichier", "Aléatoire", "ID personnalisé"]
    )
    
    embedding = None
    custom_anchor_ids = []
    
    if embedding_source == "Fichier":
        uploaded_file = st.sidebar.file_uploader("Charger un embedding", type=["json", "txt"])
        if uploaded_file:
            embedding = load_embedding_from_file(uploaded_file)
            if embedding is not None:
                st.sidebar.success(f"Embedding chargé avec succès: {embedding.shape}")
    elif embedding_source == "Aléatoire":
        if st.sidebar.button("Générer un embedding aléatoire"):
            embedding = generate_random_embedding()
            st.sidebar.success(f"Embedding aléatoire généré: {embedding.shape}")
    else:  # ID personnalisé
        st.sidebar.markdown("""
        Entrez un ou plusieurs IDs de nœuds d'ancrage (un par ligne).
        
        Format: `occupation::key_15817` ou `skill::key_12345`
        """)
        custom_ids_input = st.sidebar.text_area("IDs des nœuds d'ancrage", height=100)
        if custom_ids_input:
            custom_anchor_ids = [id.strip() for id in custom_ids_input.split('\n') if id.strip()]
            if custom_anchor_ids:
                st.sidebar.success(f"{len(custom_anchor_ids)} ID(s) d'ancrage saisi(s)")
    
    # Type d'embedding à utiliser
    embedding_type = st.sidebar.selectbox(
        "Type d'embedding",
        ["esco_embedding", "esco_embedding_occupation", "esco_embedding_skill", "esco_embedding_skillsgroup"],
        index=0
    )
    
    # Paramètres de la traversée
    st.sidebar.subheader("Traversée du graphe")
    max_depth = st.sidebar.slider("Profondeur maximale", 1, 20, 10)
    min_similarity = st.sidebar.slider("Similarité minimale", 0.0, 1.0, 0.7, 0.05)
    max_nodes_per_level = st.sidebar.slider("Nœuds maximum par niveau", 1, 10, 5)
    
    # Paramètres de la recherche d'ancrage
    st.sidebar.subheader("Recherche d'ancrage")
    top_k = st.sidebar.slider("Nombre de nœuds d'ancrage", 1, 10, 5)
    threshold = st.sidebar.slider("Seuil de similarité", 0.0, 1.0, 0.3, 0.05)
    
    # Filtres de type de nœud
    st.sidebar.subheader("Type d'ancrage")
    anchor_type = st.sidebar.selectbox(
        "Sélectionner le type d'ancrage",
        [
            "Tous les types",
            "Occupations seulement",
            "Groupes d'occupations seulement",
            "Compétences seulement",
            "Groupes de compétences seulement"
        ],
        index=0
    )
    
    # Définir les types de filtres en fonction de la sélection
    filter_types = []
    if anchor_type == "Tous les types":
        filter_types = ["occupation", "occupation_group", "skill", "skillgroup"]
    elif anchor_type == "Occupations seulement":
        filter_types = ["occupation"]
    elif anchor_type == "Groupes d'occupations seulement":
        filter_types = ["occupation_group"]  # Modifié pour correspondre au nom dans Pinecone
    elif anchor_type == "Compétences seulement":
        filter_types = ["skill"]
    elif anchor_type == "Groupes de compétences seulement":
        filter_types = ["skillgroup"]
    
    # Afficher les types sélectionnés
    st.sidebar.info(f"Types d'ancrage sélectionnés: {', '.join(filter_types)}")
    
    # Bouton pour lancer la traversée
    if (embedding is not None or custom_anchor_ids) and st.sidebar.button("Lancer la traversée"):
        # Initialiser la liste des IDs d'ancrage
        anchor_ids = []
        
        # Si nous utilisons des IDs personnalisés
        if embedding_source == "ID personnalisé":
            anchor_ids = custom_anchor_ids
            
            # Vérifier si les IDs existent dans le graphe
            valid_ids = [node_id for node_id in anchor_ids if node_id in graph_service.graph.nodes]
            invalid_ids = [node_id for node_id in anchor_ids if node_id not in graph_service.graph.nodes]
            
            if invalid_ids:
                st.warning(f"Les IDs suivants n'existent pas dans le graphe et seront ignorés: {', '.join(invalid_ids)}")
            
            if not valid_ids:
                st.error("Aucun ID d'ancrage valide. Veuillez vérifier les IDs saisis.")
                return
            
            anchor_ids = valid_ids
            
            # Créer une liste d'ancres pour l'affichage
            anchors = []
            for node_id in anchor_ids:
                node_info = graph_service.get_node_info(node_id)
                anchors.append({
                    "id": node_id,
                    "metadata": {
                        "label": node_info.get("preferredlabel", node_info.get("label", "")),
                        "type": node_info.get("type", "unknown")
                    },
                    "score": 1.0  # Score par défaut pour les IDs personnalisés
                })
        else:
            # Afficher un spinner pendant le traitement
            with st.spinner("Recherche des nœuds d'ancrage..."):
                # Trouver les nœuds d'ancrage
                anchors = anchor_service.find_anchors(
                    embedding=embedding,
                    top_k=top_k,
                    threshold=threshold,
                    filter_types=filter_types
                )
                
                if not anchors:
                    st.error("Aucun nœud d'ancrage trouvé. Essayez de réduire le seuil de similarité.")
                    return
                
                # Extraire les IDs des nœuds d'ancrage
                anchor_ids = [anchor["id"] for anchor in anchors]
            
            # Afficher les nœuds d'ancrage
            st.subheader("Nœuds d'ancrage")
            anchors_df = pd.DataFrame([
                {
                    "ID": anchor["id"],
                    "Label": anchor["metadata"].get("preferredlabel", anchor["metadata"].get("label", "")),
                    "Type": anchor["metadata"].get("type", "unknown"),
                    "Score": anchor["score"]
                }
                for anchor in anchors
            ])
            st.dataframe(anchors_df, use_container_width=True)
        
        # Traverser le graphe
        with st.spinner("Traversée du graphe en cours..."):
            start_time = time.time()
            
            graph_data = graph_service.traverse_graph(
                anchor_node_ids=anchor_ids,
                max_depth=max_depth,
                min_similarity=min_similarity,
                max_nodes_per_level=max_nodes_per_level
            )
            
            elapsed_time = time.time() - start_time
            
            if not graph_data.get("nodes"):
                st.error("Aucun nœud trouvé lors de la traversée du graphe.")
                return
            
            # Afficher les statistiques du graphe
            st.subheader("Statistiques du graphe")
            st.write(f"Temps de traversée: {elapsed_time:.2f} secondes")
            st.write(f"Nombre de nœuds: {len(graph_data.get('nodes', {}))}")
            st.write(f"Nombre d'arêtes: {len(graph_data.get('edges', []))}")
            
            # Afficher le graphe
            st.subheader("Visualisation du graphe")
            display_plotly_graph(graph_data)
            
            # Afficher les informations des nœuds
            st.subheader("Informations des nœuds")
            display_nodes_info(graph_data)
            
            # Exporter le graphe
            st.subheader("Exporter le graphe")
            col1, col2 = st.columns(2)
            
            with col1:
                # Exporter au format JSON
                json_str = json.dumps(graph_data, indent=2)
                b64 = base64.b64encode(json_str.encode()).decode()
                href = f'<a href="data:file/json;base64,{b64}" download="skill_tree.json">Télécharger le graphe (JSON)</a>'
                st.markdown(href, unsafe_allow_html=True)
            
            with col2:
                # Exporter l'image du graphe
                img_base64 = viz_service.visualize_matplotlib(graph_data)
                if img_base64:
                    href = f'<a href="data:image/png;base64,{img_base64}" download="skill_tree.png">Télécharger l\'image du graphe (PNG)</a>'
                    st.markdown(href, unsafe_allow_html=True)
    
    # Afficher des instructions si aucun embedding n'est fourni
    else:
        st.info("Veuillez fournir un embedding ou générer un embedding aléatoire, puis cliquer sur 'Lancer la traversée'.")
        
        # Afficher un exemple de graphe
        st.subheader("Exemple de visualisation")
        st.image("https://miro.medium.com/max/1400/1*hZlGq5lH5nGBhN33hO3E1Q.png", 
                caption="Exemple de graphe de compétences")

# Point d'entrée de l'application
if __name__ == "__main__":
    main()