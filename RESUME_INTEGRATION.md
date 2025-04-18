# Reactive Resume Integration Guide

This guide explains how Orientor integrates with Reactive Resume to provide professional resume building functionality for your users.

## Overview

The integration uses Reactive Resume, an open-source resume builder, self-hosted alongside Orientor. Key features:

- **Single Sign-On**: Users log in once to Orientor and can access the resume builder without a separate login
- **Profile Data Integration**: User's profile data from Orientor is automatically used to pre-fill resume fields
- **Embedded Experience**: Resume builder is embedded right within the Orientor platform

## Setup Instructions

### 1. Clone and Configure Reactive Resume

The easiest way to set up Reactive Resume is to use the provided script:

```bash
./run-resume.sh
```

This script will:
- Clone the Reactive Resume repository (if not already done)
- Create environment configuration
- Start Reactive Resume with Docker Compose

Alternatively, you can manually set up Reactive Resume:

```bash
git clone https://github.com/AmruthPillai/Reactive-Resume.git
cd Reactive-Resume
cp .env.example .env
# Edit .env file with your configuration
docker-compose -f compose.yml up --build
```

### 2. Environment Configuration

Make sure these environment variables are set in your backend `.env` file:

```
# Reactive Resume integration
REACTIVE_RESUME_API_URL=http://localhost:3100/api
REACTIVE_RESUME_JWT_SECRET=your-secret-key  # Must match Reactive Resume's SECRET_KEY
```

And in your frontend `.env.local`:

```
NEXT_PUBLIC_REACTIVE_RESUME_URL=http://localhost:3100
```

### 3. Authentication Flow

The integration uses JWT tokens for authentication:

1. When a user logs into Orientor, they receive a JWT token
2. When accessing the Resume Builder, this token is passed to the backend
3. The backend validates the token and generates a compatible token for Reactive Resume
4. This token is used to authenticate with Reactive Resume's API

## Usage

Users can access the Resume Builder through:

1. The "Resume Builder" link in the navigation menu
2. Directly visiting `/cv` in your application

## API Endpoints

Backend endpoints for integration:

- `GET /resume/generate-token` - Generates a token for Reactive Resume
- `POST /resume/create` - Creates a new resume using the user's profile data
- `GET /resume/list` - Lists all resumes for the current user

## Customization

You can customize the resume templates and available sections by modifying:

1. The `map_profile_to_resume` function in `backend/app/routers/resume.py`
2. The Reactive Resume templates (see Reactive Resume documentation)

## Troubleshooting

Common issues:

1. **Authentication errors**: Ensure the JWT secret keys match between Orientor and Reactive Resume
2. **CORS errors**: Make sure Reactive Resume's domain is added to the allowed origins in your FastAPI CORS middleware
3. **Empty resumes**: Check that the mapping function is correctly pulling data from user profiles

## Security Considerations

This integration passes authentication tokens between systems. Ensure:

1. All communication is over HTTPS in production
2. JWT secrets are kept secure and not exposed
3. Database access is properly secured

## Next Steps

Consider these enhancements:

1. Add ability to export resumes as PDF directly from Orientor
2. Add resume templates specific to different career paths
3. Integrate resume builder into the career recommendation workflow 