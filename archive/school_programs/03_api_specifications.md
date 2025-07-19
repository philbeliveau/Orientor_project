# School Programs API Specifications

## Overview

This document defines the REST API specifications for the school programs integration module. The API follows RESTful principles and integrates seamlessly with the existing Orientor platform architecture.

## Base Configuration

```yaml
API_VERSION: v1
BASE_PATH: /api/v1/school-programs
AUTHENTICATION: Bearer Token (JWT)
CONTENT_TYPE: application/json
RATE_LIMIT: 1000 requests/hour per user
```

## Authentication

All endpoints require authentication using the existing Orientor user authentication system:

```http
Authorization: Bearer <jwt_token>
```

## Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid search parameters",
    "details": {
      "field": "location",
      "reason": "Country code must be ISO 3166-1 alpha-2 format"
    },
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

## Data Models

### Program Model

```json
{
  "id": "uuid",
  "title": "Computer Science and Technology",
  "title_fr": "Techniques de l'informatique",
  "description": "Program description in English",
  "description_fr": "Description du programme en français",
  "institution": {
    "id": "uuid",
    "name": "Dawson College",
    "name_fr": "Collège Dawson",
    "type": "cegep",
    "city": "Montreal",
    "province": "Quebec",
    "country": "Canada",
    "website": "https://www.dawsoncollege.qc.ca"
  },
  "program_details": {
    "type": "technical",
    "level": "diploma",
    "duration_months": 36,
    "language": ["en", "fr"],
    "cip_code": "11.0201",
    "isced_code": "0613",
    "program_code": "420B0"
  },
  "classification": {
    "field_of_study": "Computer and Information Sciences",
    "field_of_study_fr": "Sciences informatiques et de l'information",
    "category": "STEM",
    "subcategory": "Technology"
  },
  "admission": {
    "requirements": [
      "Quebec Secondary School Diploma",
      "Mathematics 526"
    ],
    "requirements_fr": [
      "Diplôme d'études secondaires du Québec",
      "Mathématiques 526"
    ],
    "deadline": "2025-03-01",
    "application_method": "SRAM"
  },
  "academic_info": {
    "credits": 91.33,
    "semester_count": 6,
    "internship_required": true,
    "coop_available": false
  },
  "career_outcomes": {
    "job_titles": [
      "Software Developer",
      "Systems Analyst",
      "Database Administrator"
    ],
    "employment_rate": 0.89,
    "average_salary": {
      "min": 45000,
      "max": 65000,
      "currency": "CAD"
    }
  },
  "costs": {
    "tuition_per_semester": 183,
    "total_program_cost": 1098,
    "currency": "CAD",
    "financial_aid_available": true
  },
  "metadata": {
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T12:45:00Z",
    "last_synced": "2025-01-15T12:45:00Z",
    "source": "sram",
    "source_url": "https://www.sram.qc.ca/..."
  }
}
```

### Search Query Model

```json
{
  "text": "computer science",
  "filters": {
    "program_type": ["cegep", "university"],
    "level": ["diploma", "bachelor"],
    "location": {
      "country": "CA",
      "province": "QC",
      "city": "Montreal"
    },
    "language": ["en", "fr"],
    "duration": {
      "min_months": 12,
      "max_months": 48
    },
    "field_of_study": ["Computer Science", "Engineering"],
    "institution_type": ["public", "private"],
    "costs": {
      "max_tuition": 10000,
      "currency": "CAD"
    }
  },
  "sort": {
    "field": "relevance",
    "direction": "desc"
  },
  "pagination": {
    "page": 1,
    "limit": 20
  }
}
```

### Search Results Model

```json
{
  "results": [
    "... array of Program objects ..."
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_pages": 15,
    "total_results": 287,
    "has_next": true,
    "has_previous": false
  },
  "facets": {
    "program_type": {
      "cegep": 156,
      "university": 131
    },
    "level": {
      "diploma": 156,
      "bachelor": 98,
      "master": 33
    },
    "province": {
      "Quebec": 189,
      "Ontario": 98
    }
  },
  "metadata": {
    "search_time_ms": 234,
    "sources_queried": ["sram", "college_scorecard", "waterloo_api"],
    "cache_hit": false
  }
}
```

## API Endpoints

### 1. Program Search

#### Search Programs
```http
POST /api/v1/school-programs/search
```

**Request Body:**
```json
{
  "text": "computer science",
  "filters": {
    "program_type": ["cegep", "university"],
    "location": {
      "country": "CA",
      "province": "QC"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [...],
    "pagination": {...},
    "facets": {...}
  }
}
```

#### Quick Search (GET)
```http
GET /api/v1/school-programs/search?q=computer+science&type=cegep&province=QC
```

### 2. Program Details

#### Get Program by ID
```http
GET /api/v1/school-programs/programs/{program_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "... Program object ..."
  }
}
```

#### Get Programs by Institution
```http
GET /api/v1/school-programs/institutions/{institution_id}/programs
```

### 3. Program Classification

#### Get Classification Hierarchy
```http
GET /api/v1/school-programs/classifications/{system}
```

**Parameters:**
- `system`: `cip` | `isced` | `custom`

**Response:**
```json
{
  "success": true,
  "data": {
    "system": "cip",
    "version": "2021",
    "hierarchy": [
      {
        "code": "11",
        "title": "Computer and Information Sciences and Support Services",
        "children": [
          {
            "code": "11.01",
            "title": "Computer and Information Sciences, General",
            "children": [...]
          }
        ]
      }
    ]
  }
}
```

#### Map Classification Codes
```http
POST /api/v1/school-programs/classifications/map
```

**Request:**
```json
{
  "from_system": "cip",
  "to_system": "isced",
  "codes": ["11.0201", "14.0901"]
}
```

### 4. Institutions

#### List Institutions
```http
GET /api/v1/school-programs/institutions
```

**Query Parameters:**
- `type`: `cegep` | `university` | `college`
- `country`: ISO 3166-1 alpha-2 country code
- `province`: Province/state code
- `limit`: Results per page (default: 50, max: 100)
- `offset`: Pagination offset

#### Get Institution Details
```http
GET /api/v1/school-programs/institutions/{institution_id}
```

### 5. User Program Interactions

#### Save Program
```http
POST /api/v1/school-programs/users/saved-programs
```

**Request:**
```json
{
  "program_id": "uuid",
  "notes": "Interested in this program for fall admission"
}
```

#### Get Saved Programs
```http
GET /api/v1/school-programs/users/saved-programs
```

#### Remove Saved Program
```http
DELETE /api/v1/school-programs/users/saved-programs/{program_id}
```

#### Record Program Interaction
```http
POST /api/v1/school-programs/users/interactions
```

**Request:**
```json
{
  "program_id": "uuid",
  "interaction_type": "viewed",
  "metadata": {
    "source": "search_results",
    "position": 3
  }
}
```

### 6. Recommendations

#### Get Program Recommendations
```http
GET /api/v1/school-programs/users/recommendations
```

**Query Parameters:**
- `limit`: Number of recommendations (default: 10, max: 50)
- `include_reasons`: Include recommendation reasoning (boolean)

**Response:**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "program": {...},
        "score": 0.89,
        "reasons": [
          "Matches your Holland profile (Investigative)",
          "Located in your preferred region",
          "Strong career outcomes in technology"
        ]
      }
    ],
    "metadata": {
      "recommendation_model": "v2.1",
      "generated_at": "2025-01-15T10:30:00Z"
    }
  }
}
```

### 7. Program Comparison

#### Compare Programs
```http
POST /api/v1/school-programs/compare
```

**Request:**
```json
{
  "program_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "programs": [...],
    "comparison_matrix": {
      "duration": [36, 48, 24],
      "tuition": [1098, 3500, 800],
      "employment_rate": [0.89, 0.92, 0.78]
    }
  }
}
```

### 8. Filters and Facets

#### Get Available Filters
```http
GET /api/v1/school-programs/filters
```

**Response:**
```json
{
  "success": true,
  "data": {
    "program_types": [
      {"value": "cegep", "label": "CEGEP", "count": 1247},
      {"value": "university", "label": "University", "count": 2891}
    ],
    "provinces": [
      {"value": "QC", "label": "Quebec", "count": 856},
      {"value": "ON", "label": "Ontario", "count": 1234}
    ],
    "fields_of_study": [...],
    "levels": [...],
    "languages": [...]
  }
}
```

## Advanced Features

### 1. Autocomplete/Suggestions

#### Program Title Suggestions
```http
GET /api/v1/school-programs/suggestions/programs?q=comput
```

#### Institution Name Suggestions
```http
GET /api/v1/school-programs/suggestions/institutions?q=dawson
```

### 2. Batch Operations

#### Get Multiple Programs
```http
POST /api/v1/school-programs/programs/batch
```

**Request:**
```json
{
  "program_ids": ["uuid1", "uuid2", "uuid3"]
}
```

### 3. Export Data

#### Export Search Results
```http
POST /api/v1/school-programs/export
```

**Request:**
```json
{
  "search_query": {...},
  "format": "csv",
  "fields": ["title", "institution", "duration", "tuition"]
}
```

## WebSocket Real-time Updates

### Program Status Updates
```javascript
// Connect to WebSocket
const ws = new WebSocket('wss://api.orientor.com/ws/school-programs');

// Subscribe to program updates
ws.send(JSON.stringify({
  type: 'subscribe',
  topic: 'program_updates',
  filters: {
    program_ids: ['uuid1', 'uuid2']
  }
}));

// Receive updates
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // {
  //   type: 'program_updated',
  //   program_id: 'uuid1',
  //   changes: {
  //     admission_deadline: '2025-04-01'
  //   }
  // }
};
```

## Rate Limiting

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642291200
```

### Rate Limit Exceeded Response
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "details": {
      "limit": 1000,
      "window": "1 hour",
      "reset_at": "2025-01-15T11:00:00Z"
    }
  }
}
```

## Caching Strategy

### Cache Headers
```http
Cache-Control: public, max-age=3600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Last-Modified: Wed, 15 Jan 2025 10:30:00 GMT
```

### Conditional Requests
```http
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"
If-Modified-Since: Wed, 15 Jan 2025 10:30:00 GMT
```

## API Versioning

### Version in URL
```http
GET /api/v1/school-programs/search
GET /api/v2/school-programs/search
```

### Version in Header
```http
Accept: application/vnd.orientor.v1+json
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `EXTERNAL_SERVICE_ERROR` | 502 | External API unavailable |
| `SERVICE_TEMPORARILY_UNAVAILABLE` | 503 | Service maintenance |

## OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: Orientor School Programs API
  version: 1.0.0
  description: API for searching and managing school programs
  contact:
    name: Orientor Development Team
    email: dev@orientor.com

servers:
  - url: https://api.orientor.com/api/v1/school-programs
    description: Production server
  - url: https://staging-api.orientor.com/api/v1/school-programs
    description: Staging server

paths:
  /search:
    post:
      summary: Search for programs
      tags:
        - Programs
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SearchQuery'
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SearchResults'
        '400':
          description: Invalid search parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    Program:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
        # ... other properties
    
    SearchQuery:
      type: object
      properties:
        text:
          type: string
        filters:
          type: object
        # ... other properties
    
    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: object

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
```

## Integration with Orientor Platform

### User Profile Integration
- Use existing user authentication system
- Leverage Holland RIASEC profiles for program recommendations
- Integrate with personality assessments for better matching

### Skill Tree Integration
- Map program requirements to existing skill nodes
- Generate learning paths that include formal education options
- Connect program outcomes to career skill development

### Recommendation Engine Integration
- Use collaborative filtering based on user interactions
- Content-based filtering using program attributes
- Hybrid approach combining multiple recommendation strategies

This API specification provides a comprehensive foundation for integrating school program data into the Orientor platform while maintaining consistency with existing architectural patterns and user experience paradigms.