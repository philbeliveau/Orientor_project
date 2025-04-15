import os
import csv
from dotenv import load_dotenv
from typing import Dict
from pinecone import Pinecone  # Pinecone v3+

load_dotenv()

# === Config ===
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "oasis-minilm-index"
CSV_PATH = "/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/data_n_notebook/data/KnowledgeBase/KnowledgeBase.csv"
BATCH_SIZE = 96

# ✅ Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

def combine_row_text(row: Dict[str, str]) -> str:
    text_parts = []

    if row.get("Label"):
        text_parts.append(f"Occupation: {row['Label']}")
    if row.get("Lead statement"):
        text_parts.append(f"Description: {row['Lead statement']}")
    if row.get("Main duties"):
        text_parts.append(f"Main duties: {row['Main duties']}")

    for col in ["Creativity", "Leadership", "Digital Literacy", "Critical Thinking", "Problem Solving"]:
        if row.get(col):
            text_parts.append(f"{col}: {row[col]}")

    return ". ".join(text_parts).strip()

def main():
    print(f"🚀 Upserting raw text to Pinecone index: {INDEX_NAME} (using integrated embedding)")
    total_processed = 0
    batch_records = []

    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader):
                if not row or not row.get("oasis_code"):
                    continue

                text = combine_row_text(row)
                if not text:
                    continue

                # Create vector object (raw text, no values)
                doc_id = f"oasis-{row.get('oasis_code', '').strip()}-{row.get('Concordance number', str(i)).strip()}"
                
                # Create vector object for integrated embeddings - keeping it simple like the docs
                vector = {
                    "id": doc_id,
                    "text": text
                }
                
                batch_records.append(vector)

                if len(batch_records) >= BATCH_SIZE:
                    try:
                        index.upsert_records(namespace="", records=batch_records)
                        total_processed += len(batch_records)
                        print(f"✅ Upserted batch of {len(batch_records)}. Total so far: {total_processed}")
                    except Exception as e:
                        print(f"❌ Batch error: {e}")
                        print(f"First record in failed batch: {batch_records[0]}")
                    batch_records = []

            if batch_records:
                try:
                    index.upsert_records(namespace="", records=batch_records)
                    total_processed += len(batch_records)
                    print(f"✅ Final upsert of {len(batch_records)}. Total uploaded: {total_processed}")
                except Exception as e:
                    print(f"❌ Final batch error: {e}")
                    print(f"First record in failed batch: {batch_records[0]}")

        print("🎉 All done! Data embedded and upserted into Pinecone.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
