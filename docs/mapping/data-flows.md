# Data Flow Diagrams - User Journeys & System Interactions

## 🔄 **Core System Data Flows**

### **User Onboarding Flow**

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 📱 Frontend
    participant API as 🔧 API Gateway  
    participant AUTH as 🔐 Auth Service
    participant AI as 🤖 Orientator AI
    participant ASSESS as 📊 Assessment Service
    participant EMBED as 📊 Embedding Service
    participant DB as 🗄️ Database
    
    U->>F: Access /onboarding
    F->>API: POST /auth/register
    API->>AUTH: Create User Account
    AUTH->>DB: Store User Data
    DB-->>AUTH: User Created
    AUTH-->>API: JWT Token
    API-->>F: Authentication Success
    
    F->>U: Display Chat Onboarding
    U->>F: Answer Questions
    F->>API: POST /onboarding/responses
    API->>AI: Process Responses
    AI->>ASSESS: Analyze Psychological Profile
    ASSESS->>EMBED: Generate User Embeddings
    EMBED-->>ASSESS: Vector Representation
    ASSESS-->>AI: Profile Complete
    AI->>DB: Store Profile & Embeddings
    AI-->>API: Onboarding Complete
    API-->>F: Success Response
    F->>U: Redirect to Dashboard
```

### **Career Recommendation Flow**

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 📱 Frontend
    participant API as 🔧 API Gateway
    participant AI as 🤖 Orientator AI
    participant TOOLS as 🔨 Tool Registry
    participant ESCO as 📊 ESCO Service
    participant OASIS as 🔍 OASIS Service
    participant GNN as 🕸️ GraphSage
    participant DB as 🗄️ Database
    
    U->>F: Request Career Recommendations
    F->>API: GET /recommendations
    API->>AI: Generate Recommendations
    AI->>DB: Get User Profile
    DB-->>AI: User Data & Embeddings
    
    AI->>TOOLS: Invoke OASIS Tool
    TOOLS->>OASIS: Search Similar Careers
    OASIS->>DB: Query Career Database
    DB-->>OASIS: Career Matches
    OASIS-->>TOOLS: Ranked Results
    
    AI->>TOOLS: Invoke ESCO Tool
    TOOLS->>ESCO: Get Required Skills
    ESCO->>DB: Query Skills Database
    DB-->>ESCO: Skills Data
    ESCO-->>TOOLS: Skills Analysis
    
    AI->>TOOLS: Invoke Career Tree Tool
    TOOLS->>GNN: Generate Career Paths
    GNN->>DB: Graph Traversal
    DB-->>GNN: Path Data
    GNN-->>TOOLS: Career Trees
    
    TOOLS-->>AI: Combined Results
    AI->>DB: Store Recommendations
    AI-->>API: Structured Response
    API-->>F: Career Cards + Trees
    F->>U: Interactive Display
```

### **Assessment Processing Flow**

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 📱 Frontend
    participant API as 🔧 API Gateway
    participant HEXACO as 🧠 HEXACO Router
    participant LLM_H as 🧠 HEXACO LLM Service
    participant SCORING as 📈 Scoring Service
    participant EMBED as 📊 Embedding Service
    participant AI as 🤖 Orientator AI
    participant DB as 🗄️ Database
    
    U->>F: Take HEXACO Test
    F->>API: POST /hexaco-test/submit
    API->>HEXACO: Process Responses
    HEXACO->>LLM_H: Analyze Responses
    LLM_H->>SCORING: Calculate Scores
    SCORING-->>LLM_H: Trait Scores
    LLM_H->>EMBED: Generate Personality Vector
    EMBED-->>LLM_H: Vector Embedding
    LLM_H-->>HEXACO: Complete Profile
    
    HEXACO->>DB: Store Assessment Results
    HEXACO->>AI: Update User Model
    AI->>DB: Update User Representation
    
    HEXACO-->>API: Assessment Complete
    API-->>F: Results + Insights
    F->>U: Personality Dashboard
```

### **Interactive Tree Navigation Flow**

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 📱 Frontend
    participant API as 🔧 API Gateway
    participant TREE as 🌳 Tree Router
    participant COMPETENCE as 🌿 Competence Service
    participant GNN as 🕸️ GraphSage
    participant CACHE as ⚡ Cache Layer
    participant DB as 🗄️ Database
    
    U->>F: Open Competence Tree
    F->>API: GET /competence-tree
    API->>TREE: Initialize Tree
    TREE->>CACHE: Check Cached Tree
    alt Cache Hit
        CACHE-->>TREE: Cached Tree Data
    else Cache Miss
        TREE->>COMPETENCE: Generate Tree
        COMPETENCE->>DB: Get User Skills
        DB-->>COMPETENCE: Skills Data
        COMPETENCE->>GNN: Build Graph
        GNN-->>COMPETENCE: Tree Structure
        COMPETENCE->>CACHE: Store Tree
        COMPETENCE-->>TREE: New Tree Data
    end
    
    TREE-->>API: Tree Response
    API-->>F: Tree JSON + Metadata
    F->>U: Interactive Visualization
    
    U->>F: Click Node
    F->>API: POST /tree-paths/navigate
    API->>TREE: Log Navigation
    TREE->>DB: Store Path Data
    TREE->>COMPETENCE: Get Node Details
    COMPETENCE->>DB: Query Node Info
    DB-->>COMPETENCE: Node Data
    COMPETENCE-->>TREE: Node Details
    TREE-->>API: Node Response
    API-->>F: Node Modal Data
    F->>U: Display Node Details
```

### **Chat Intelligence Flow**

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 📱 Frontend
    participant API as 🔧 API Gateway
    participant CHAT as 💬 Chat Router
    participant AI as 🤖 Orientator AI
    participant TOOLS as 🔨 Tool Registry
    participant LLM as 🧠 OpenAI LLM
    participant MEMORY as 🧠 Memory System
    participant DB as 🗄️ Database
    
    U->>F: Send Chat Message
    F->>API: POST /chat/message
    API->>CHAT: Process Message
    CHAT->>AI: Analyze Intent
    
    AI->>MEMORY: Get Conversation Context
    MEMORY->>DB: Retrieve History
    DB-->>MEMORY: Previous Messages
    MEMORY-->>AI: Context Data
    
    AI->>LLM: Generate Response
    LLM-->>AI: Response + Tool Calls
    
    alt Tool Invocation Required
        AI->>TOOLS: Invoke Tools
        TOOLS->>DB: Execute Tool Logic
        DB-->>TOOLS: Tool Results
        TOOLS-->>AI: Tool Outputs
        AI->>LLM: Incorporate Tool Results
        LLM-->>AI: Final Response
    end
    
    AI->>DB: Store Message & Components
    AI->>MEMORY: Update Context
    AI-->>CHAT: Structured Response
    CHAT-->>API: Message + Components
    API-->>F: Streaming Response
    F->>U: Real-time Display
```

## 🎓 **Education Integration Flow**

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 📱 Frontend
    participant API as 🔧 API Gateway
    participant EDU as 🎓 Education Router
    participant PROGRAM as 📚 Program Service
    participant MATCH as 🎯 Matching Engine
    participant EXTERNAL as 🏫 School APIs
    participant DB as 🗄️ Database
    
    U->>F: Browse Programs
    F->>API: GET /education/programs
    API->>EDU: Get Program Recommendations
    EDU->>DB: Get User Profile
    DB-->>EDU: User Data
    
    EDU->>PROGRAM: Find Matching Programs
    PROGRAM->>MATCH: Calculate Compatibility
    MATCH->>DB: Query Programs Database
    DB-->>MATCH: Program Data
    MATCH-->>PROGRAM: Ranked Programs
    
    PROGRAM->>EXTERNAL: Get Real-time Data
    EXTERNAL-->>PROGRAM: Updated Info
    PROGRAM-->>EDU: Enhanced Results
    
    EDU-->>API: Program List
    API-->>F: Program Cards
    F->>U: Interactive Display
    
    U->>F: Select Program
    F->>API: POST /education/programs/save
    API->>EDU: Save Interest
    EDU->>DB: Store User Interest
    EDU-->>API: Confirmation
    API-->>F: Success Response
    F->>U: Added to Saved Programs
```

## 👥 **Peer Matching Flow**

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 📱 Frontend
    participant API as 🔧 API Gateway
    participant PEERS as 👥 Peers Router
    participant MATCHING as 🤝 Peer Matching Service
    participant GRAPH as 🌐 Social Graph
    participant PRIVACY as 🛡️ Privacy Filter
    participant DB as 🗄️ Database
    
    U->>F: Find Peers
    F->>API: GET /peers/recommendations
    API->>PEERS: Generate Peer Matches
    PEERS->>DB: Get User Profile
    DB-->>PEERS: User Data
    
    PEERS->>MATCHING: Find Compatible Peers
    MATCHING->>DB: Query User Vectors
    DB-->>MATCHING: User Embeddings
    MATCHING->>GRAPH: Analyze Connections
    GRAPH-->>MATCHING: Network Data
    
    MATCHING->>PRIVACY: Filter Results
    PRIVACY->>DB: Check Privacy Settings
    DB-->>PRIVACY: Consent Data
    PRIVACY-->>MATCHING: Filtered Matches
    
    MATCHING-->>PEERS: Peer Recommendations
    PEERS-->>API: Anonymized Matches
    API-->>F: Peer Cards
    F->>U: Potential Connections
    
    U->>F: Connect with Peer
    F->>API: POST /peers/connect
    API->>PEERS: Initiate Connection
    PEERS->>DB: Store Connection Request
    PEERS-->>API: Request Sent
    API-->>F: Connection Pending
    F->>U: Request Sent Notification
```

## 📊 **Real-time Analytics Flow**

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 📱 Frontend
    participant API as 🔧 API Gateway
    participant ANALYTICS as 📊 Analytics Service
    participant STREAM as 🌊 Event Stream
    participant PROCESSOR as ⚡ Data Processor
    participant AGGREGATOR as 📈 Aggregator
    participant DB as 🗄️ Database
    
    U->>F: User Action (Click, View, etc.)
    F->>API: Track Event
    API->>ANALYTICS: Log User Event
    ANALYTICS->>STREAM: Publish Event
    
    STREAM->>PROCESSOR: Process Event
    PROCESSOR->>DB: Update Raw Events
    PROCESSOR->>AGGREGATOR: Aggregate Metrics
    
    AGGREGATOR->>DB: Update Aggregated Data
    AGGREGATOR->>STREAM: Publish Insights
    
    alt Real-time Dashboard Update
        STREAM->>API: Dashboard Event
        API->>F: WebSocket Update
        F->>U: Live Dashboard Update
    end
    
    alt Batch Processing
        PROCESSOR->>DB: Generate Reports
        DB-->>PROCESSOR: Historical Data
        PROCESSOR->>AGGREGATOR: Batch Insights
        AGGREGATOR->>DB: Store Insights
    end
```

## 🔍 **Vector Search Flow**

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 📱 Frontend
    participant API as 🔧 API Gateway
    participant SEARCH as 🔍 Vector Search Router
    participant EMBED as 📊 Embedding Service
    participant INDEX as 📇 Vector Index
    participant RANK as 📈 Ranking Engine
    participant DB as 🗄️ Database
    
    U->>F: Enter Search Query
    F->>API: POST /vector-search
    API->>SEARCH: Process Search
    SEARCH->>EMBED: Vectorize Query
    EMBED-->>SEARCH: Query Vector
    
    SEARCH->>INDEX: Similarity Search
    INDEX->>DB: Retrieve Vectors
    DB-->>INDEX: Vector Data
    INDEX-->>SEARCH: Similar Vectors
    
    SEARCH->>RANK: Rank Results
    RANK->>DB: Get Entity Details
    DB-->>RANK: Entity Data
    RANK-->>SEARCH: Ranked Results
    
    SEARCH-->>API: Search Results
    API-->>F: Formatted Results
    F->>U: Search Results Display
```

## 🔄 **System Health Monitoring Flow**

```mermaid
sequenceDiagram
    participant MONITOR as 📊 Health Monitor
    participant SERVICES as 🛠️ Services
    participant DB as 🗄️ Database
    participant CACHE as ⚡ Cache
    participant EXTERNAL as 🌐 External APIs
    participant ALERTS as 🚨 Alert System
    participant ADMIN as 👨‍💼 Admin Dashboard
    
    loop Every 30 seconds
        MONITOR->>SERVICES: Health Check
        SERVICES-->>MONITOR: Service Status
        
        MONITOR->>DB: Connection Test
        DB-->>MONITOR: DB Status
        
        MONITOR->>CACHE: Performance Check
        CACHE-->>MONITOR: Cache Metrics
        
        MONITOR->>EXTERNAL: API Availability
        EXTERNAL-->>MONITOR: API Status
        
        alt System Issues Detected
            MONITOR->>ALERTS: Trigger Alert
            ALERTS->>ADMIN: Notify Administrators
        end
        
        MONITOR->>DB: Store Metrics
    end
```

## 🔄 **Data Synchronization Flow**

```mermaid
sequenceDiagram
    participant LOCAL as 💾 Local Database
    participant SYNC as 🔄 Sync Service
    participant CLOUD as ☁️ Cloud Database
    participant BACKUP as 💿 Backup Service
    participant CONFLICT as ⚖️ Conflict Resolver
    
    loop Every Hour
        SYNC->>LOCAL: Check for Changes
        LOCAL-->>SYNC: Changed Records
        
        SYNC->>CLOUD: Sync Changes
        CLOUD-->>SYNC: Cloud Changes
        
        alt Conflicts Detected
            SYNC->>CONFLICT: Resolve Conflicts
            CONFLICT->>LOCAL: Apply Resolution
            CONFLICT->>CLOUD: Update Cloud
        else No Conflicts
            SYNC->>LOCAL: Apply Cloud Changes
            SYNC->>CLOUD: Confirm Sync
        end
        
        SYNC->>BACKUP: Trigger Backup
        BACKUP->>CLOUD: Create Backup
    end
```

These data flow diagrams illustrate the complete system interactions and user journeys throughout the Orientor platform, showing how data moves between components and how various services collaborate to deliver the user experience.