# Agent APIs Documentation

## Overview

The Marketing Multi-Agent System exposes RESTful APIs that enable interaction with the AI-enhanced marketing automation system. All endpoints require authentication using JWT tokens.

## Authentication

Authentication is required for all API endpoints. Use the following header format:
```
Authorization: Bearer <your_jwt_token>
```

## Base URL

```
https://api.purplemerit.com/api/v1
```

## Endpoints

### Lead Management

#### Triage Lead
```http
POST /leads/{lead_id}/triage
```
AI-enhanced lead analysis and categorization.

**Request Body:**
```json
{
  "source": "string",
  "metadata": {
    "additional_info": "string"
  }
}
```

**Response:**
```json
{
  "category": "string",
  "score": number,
  "ai_insights": {
    "suggested_approach": "string",
    "key_points": ["string"],
    "predicted_conversion_probability": number
  }
}
```

### Campaign Management

#### Optimize Campaign
```http
POST /campaigns/{campaign_id}/optimize
```
AI-driven campaign optimization and recommendations.

**Response:**
```json
{
  "optimizations": [{
    "type": "string",
    "recommendation": "string",
    "impact_score": number,
    "implementation_priority": "high|medium|low"
  }],
  "ai_insights": {
    "performance_analysis": "string",
    "trend_predictions": ["string"]
  }
}
```

### Content Generation

#### Generate Content
```http
POST /content/generate
```
AI-powered personalized content generation.

**Request Body:**
```json
{
  "lead_profile": {
    "interests": ["string"],
    "engagement_history": ["string"]
  },
  "campaign_type": "string",
  "tone": "professional|casual|formal"
}
```

**Response:**
```json
{
  "content": "string",
  "variations": ["string"],
  "personalization_factors": ["string"]
}
```

### Agent Handoff

#### Handle Agent Handoff
```http
POST /agents/handoff
```
Manage agent transitions with AI-enhanced context preservation.

**Request Body:**
```json
{
  "from_agent": "string",
  "to_agent": "string",
  "lead_id": "string",
  "conversation_id": "string",
  "context": {
    "current_state": "string",
    "relevant_info": ["string"]
  }
}
```

### AI Insights

#### Get Lead Insights
```http
GET /insights/lead/{lead_id}
```
Retrieve AI-generated lead analysis and insights.

#### Get Campaign Insights
```http
GET /insights/campaign/{campaign_id}
```
Retrieve AI-generated campaign performance analysis.

#### Get Engagement Insights
```http
GET /insights/engagement/{lead_id}
```
Retrieve AI-generated engagement pattern analysis.

## Error Handling

The API uses standard HTTP status codes and returns error details in the following format:

```json
{
  "detail": "Error description"
}
```

Common status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

API requests are rate-limited based on the authentication token. Current limits:
- 100 requests per minute for standard endpoints
- 20 requests per minute for AI-enhanced endpoints

## Support

For API support or issues, contact: api-support@purplemerit.com
