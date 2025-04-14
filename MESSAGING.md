# Peer Messaging Feature

This feature allows users to exchange messages with their suggested peers, enhancing the collaborative learning experience.

## Features

- Real-time messaging between users
- Message history with timestamps
- Integration with the suggested peers system
- Clean and responsive user interface

## How It Works

1. **Suggested Peers**: Users are matched with peers based on profile similarity
2. **Conversation Initiation**: Start a conversation by clicking "Start Conversation" on a peer's card
3. **Messaging**: Exchange messages in a dedicated chat interface
4. **History**: View conversation history with proper formatting and timestamps

## Architecture

- **Database**: PostgreSQL with a messages table for storing conversations
- **Backend**: FastAPI endpoints for sending/receiving messages and retrieving conversations
- **Frontend**: React components for displaying and interacting with messages

## API Endpoints

### Messages

```
POST /messages
```
Sends a message to another user

Request body:
```json
{
  "recipient_id": 123,
  "body": "Hello, would you like to study together?"
}
```

```
GET /messages/conversation/{peer_id}
```
Gets conversation history with a specific peer

Response:
```json
[
  {
    "message_id": 1,
    "sender_id": 456,
    "recipient_id": 123,
    "body": "Hello, would you like to study together?",
    "timestamp": "2023-04-15T14:30:00Z"
  },
  {
    "message_id": 2,
    "sender_id": 123,
    "recipient_id": 456,
    "body": "Sure, I'd love to! What subject are you working on?",
    "timestamp": "2023-04-15T14:35:00Z"
  }
]
```

### Users

```
GET /users/me
```
Gets current user information

```
GET /users/{user_id}/profile
```
Gets profile information for a specific user

## Frontend Components

- **MessageList**: Displays a list of messages with proper formatting
- **MessageInput**: Input field for composing and sending messages
- **PeerChatPage**: Full chat interface with peer information

## Example Usage

1. Navigate to the Suggested Peers page (`/peers`)
2. Find a peer with similar interests
3. Click "Start Conversation"
4. Enter your message and click "Send"
5. Messages will appear in real-time with proper formatting

## Future Improvements

- Real-time messaging with WebSockets
- Message read receipts
- Typing indicators
- File/image sharing
- Group messaging for study groups 