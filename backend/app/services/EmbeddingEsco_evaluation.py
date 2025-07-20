import streamlit as st
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
import psycopg2
import json
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.parse import urlparse
import os
from pinecone import Pinecone
import ast

# --- Config ---
PINECONE_INDEX = "esco-368" # "gnn-embeddings"
DATABASE_URL = os.getenv("DATABASE_URL")

url = urlparse(DATABASE_URL)
DB_CONFIG = {
    "dbname": url.path[1:],
    "user": url.username,
    "password": url.password,
    "host": url.hostname,
    "port": url.port or 5432
}

# --- Load Node Metadata ---
with open("gnn_experiment/data/node_metadata.json") as f:
    node_metadata = json.load(f)

# --- Connect to SQL ---
def get_user_embedding(user_id, column="esco_embedding"):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(f"SELECT {column} FROM user_profiles WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    conn.close()

    if row and row[0]:
        try:
            parsed = ast.literal_eval(row[0])
            return np.array(parsed, dtype=np.float32)
        except Exception as e:
            print("Error parsing embedding:", e)
            return None
    return None

def get_user_profiles_text(user_id):
    fields = [
        "esco_occupation_profile",
        "esco_skill_profile",
        "esco_skillsgroup_profile",
        "esco_full_profile"
    ]
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(f"SELECT {', '.join(fields)} FROM user_profiles WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(zip(fields, row)) if row else {}

# --- Pinecone Diverse Query ---
def query_diverse_matches(vector):
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(PINECONE_INDEX)
    vector = np.array(vector, dtype=np.float32).tolist()

    def run_query(filter_type):
        return index.query(
            vector=vector,
            top_k=10,
            filter={"type": {"$eq": filter_type}},
            include_metadata=True,
            include_values=True
        ).matches

    return run_query("occupation") + run_query("skill") + run_query("skillgroup")

# --- Evaluate ---
def evaluate_match(user_id, expected_anchors, embedding_column):
    user_vec = get_user_embedding(user_id, column=embedding_column)
    st.write(f"Embedding type: {embedding_column}")
    st.write("Embedding shape:", user_vec.shape)
    st.write("Sample values:", user_vec[:10])

    profiles_text = get_user_profiles_text(user_id)
    for k, v in profiles_text.items():
        st.markdown(f"**{k}:**")
        st.write(v if v else "_No content available._")

    results = query_diverse_matches(user_vec)
    matches = []
    mrr = 0.0
    for i, match in enumerate(results):
        if not match.values:
            continue
        node_id = match.id
        score = 1 - cosine(user_vec, match.values)
        label = node_metadata.get(node_id, {}).get("label", "")
        is_expected = node_id in expected_anchors
        if is_expected and mrr == 0.0:
            mrr = 1 / (i + 1)
        matches.append({"rank": i + 1, "node": node_id, "label": label, "score": score, "expected": is_expected})

    precision_at_k = sum([m["expected"] for m in matches]) / len(matches)
    return matches, precision_at_k, mrr

# --- Visualization ---
def show_pca(user_vec, sample_vectors):
    pca = PCA(n_components=2)
    all_vecs = np.vstack([user_vec.reshape(1, -1), sample_vectors])
    proj = pca.fit_transform(all_vecs)
    labels = ["user"] + ["gnn"] * len(sample_vectors)
    df = pd.DataFrame({"x": proj[:, 0], "y": proj[:, 1], "label": labels})
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x="x", y="y", hue="label", ax=ax)
    st.pyplot(fig)

# --- Streamlit UI ---
st.title("User ↔️ GNN Match Evaluation")
user_id = st.number_input("Enter User ID", min_value=1, step=1)
embedding_option = st.selectbox("Select embedding type", [
    "esco_embedding", 
    "esco_embedding_occupation", 
    "esco_embedding_skill", 
    "esco_embedding_skillsgroup"
])
expected_input = st.text_input("Expected Anchors (comma-separated node IDs)")

if st.button("Run Evaluation"):
    expected_anchors = [x.strip() for x in expected_input.split(",") if x.strip()]
    with st.spinner("Evaluating matches..."):
        matches, precision, mrr = evaluate_match(user_id, expected_anchors, embedding_option)

    st.subheader("Results")
    st.write(f"**Precision@10:** {precision:.2f}")
    st.write(f"**MRR:** {mrr:.2f}")
    st.dataframe(pd.DataFrame(matches))