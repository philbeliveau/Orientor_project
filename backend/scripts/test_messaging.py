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
from app.utils.messaging import send_message, get_conversation, get_user_suggested_peers
from app.models import User, UserProfile

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
    parser = argparse.ArgumentParser(description='Test messaging functionality')
    
    parser.add_argument(
        '--user-id', '-u',
        type=int,
        required=True,
        help='ID of the user to test messaging with'
    )
    
    parser.add_argument(
        '--action', '-a',
        type=str,
        choices=['peers', 'send', 'conversation'],
        default='peers',
        help='Action to perform: find peers, send message, or view conversation'
    )
    
    parser.add_argument(
        '--peer-id', '-p',
        type=int,
        help='ID of the peer for sending a message or viewing conversation'
    )
    
    parser.add_argument(
        '--message', '-m',
        type=str,
        help='Message content for sending'
    )
    
    return parser.parse_args()

def show_user_info(db, user_id):
    """Display info about the user"""
    user = db.query(User).filter(User.id == user_id).first()
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not user:
        logger.error(f"User {user_id} not found")
        return
    
    logger.info(f"User ID: {user.id}")
    logger.info(f"Email: {user.email}")
    
    if profile:
        logger.info(f"Name: {profile.name}")
        logger.info(f"Major: {profile.major}")
        if profile.hobbies:
            logger.info(f"Hobbies: {profile.hobbies}")

def main():
    args = parse_args()
    logger.info(f"Starting action: {args.action}")
    
    db = SessionLocal()
    try:
        # Display info about the user
        show_user_info(db, args.user_id)
        
        if args.action == 'peers':
            # Get suggested peers
            peers = get_user_suggested_peers(db, args.user_id)
            
            if not peers:
                logger.info(f"No suggested peers found for user {args.user_id}")
                return 0
            
            logger.info(f"Found {len(peers)} suggested peers:")
            for i, peer in enumerate(peers):
                peer_id = peer['peer_id']
                peer_profile = db.query(UserProfile).filter(UserProfile.user_id == peer_id).first()
                peer_name = peer_profile.name if peer_profile and peer_profile.name else f"User {peer_id}"
                
                logger.info(f"{i+1}. {peer_name} (ID: {peer_id}, Similarity: {peer['similarity']:.2f})")
            
        elif args.action == 'send':
            if not args.peer_id or not args.message:
                logger.error("Peer ID and message are required for sending a message")
                return 1
            
            # Send message
            result = send_message(db, args.user_id, args.peer_id, args.message)
            
            if result:
                logger.info(f"Message sent successfully from user {args.user_id} to user {args.peer_id}")
                logger.info(f"Message ID: {result.message_id}")
            else:
                logger.error("Failed to send message")
                return 1
            
        elif args.action == 'conversation':
            if not args.peer_id:
                logger.error("Peer ID is required for viewing a conversation")
                return 1
            
            # Get conversation
            messages = get_conversation(db, args.user_id, args.peer_id)
            
            if not messages:
                logger.info(f"No messages found between users {args.user_id} and {args.peer_id}")
                return 0
            
            logger.info(f"Found {len(messages)} messages:")
            for i, msg in enumerate(messages):
                direction = "►" if msg.sender_id == args.user_id else "◄"
                logger.info(f"{i+1}. {direction} {msg.body} (Sent at: {msg.timestamp})")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    finally:
        db.close()
    
    logger.info("Operation completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 