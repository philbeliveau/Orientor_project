#!/usr/bin/env python3

import sys
import os
import argparse
import logging
from pathlib import Path

# Add the parent directory to sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from app.utils.database import SessionLocal
from app.utils.embeddings import (
    generate_and_store_embeddings,
    find_and_store_similar_peers,
    refresh_all_embeddings_and_peers
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description='Generate embeddings and find similar peers')
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='sentence-transformers/all-MiniLM-L6-v2',
        help='Sentence transformer model to use for embeddings'
    )
    
    parser.add_argument(
        '--operation', '-o',
        type=str,
        choices=['embeddings', 'peers', 'refresh'],
        default='refresh',
        help='Operation to perform: generate embeddings, find peers, or refresh both'
    )
    
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=100,
        help='Batch size for processing'
    )
    
    parser.add_argument(
        '--top-n', '-n',
        type=int,
        default=5,
        help='Number of similar peers to find for each user'
    )
    
    return parser.parse_args()

def main():
    args = parse_args()
    logger.info(f"Starting operation: {args.operation}")
    
    db = SessionLocal()
    try:
        if args.operation == 'embeddings':
            count = generate_and_store_embeddings(db, args.model)
            logger.info(f"Generated embeddings for {count} profiles")
            
        elif args.operation == 'peers':
            count = find_and_store_similar_peers(db, args.batch_size, args.top_n)
            logger.info(f"Found similar peers for {count} users")
            
        elif args.operation == 'refresh':
            result = refresh_all_embeddings_and_peers(db, args.model)
            logger.info(f"Refresh completed: {result}")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    finally:
        db.close()
    
    logger.info("Operation completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 