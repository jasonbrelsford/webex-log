# Webex Message Graph - Tech Stack

## Project Vision
A web-based SaaS platform for visualizing and querying Webex message history with graph analytics and AI-powered search.

## Architecture Overview

### Phase 1: Local Visualization (Current)
- **Goal**: Create interactive graph visualization of message data
- **Deployment**: Local Python application

### Phase 2: Web Application
- **Goal**: Multi-user web platform with authentication
- **Deployment**: Cloud-hosted (AWS/Vercel)

### Phase 3: SaaS Platform
- **Goal**: Subscription-based service with payment processing
- **Deployment**: Production-ready with monitoring

---

## Technology Stack

### Backend
- **Language**: Python 3.13+
- **Web Framework**: FastAPI (async, modern, fast)
- **API**: RESTful + WebSocket (for real-time updates)
- **Graph Database**: Neo4j (message relationships, network analysis)
- **Relational Database**: PostgreSQL (user accounts, subscriptions)
- **Cache**: Redis (session management, rate limiting)
- **Task Queue**: Celery (background message fetching)

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Library**: shadcn/ui (Tailwind CSS based)
- **Graph Visualization**: 
  - vis.js or Cytoscape.js (interactive network graphs)
  - D3.js (custom visualizations)
- **State Management**: Zustand or React Query
- **Routing**: React Router

### Authentication & Authorization
- **OAuth Provider**: Google OAuth 2.0
- **Session Management**: JWT tokens
- **Security**: HTTPS, CORS, rate limiting

### AI/LLM Integration
- **Provider**: OpenAI API (GPT-4)
- **Use Cases**:
  - Natural language message search
  - Conversation summarization
  - Topic extraction
  - Sentiment analysis

### Payment Processing
- **Provider**: Stripe
- **Payment Methods**: Credit card, Apple Pay, Google Pay
- **Subscription Model**: $12/year
- **Features**:
  - Free tier: Last 24 hours of messages
  - Paid tier: Full message history

### Data Storage & Processing
- **Message Storage**: S3-compatible object storage
- **File Format**: JSON (structured message data)
- **ETL Pipeline**: Python scripts for data transformation
- **Backup**: Automated daily backups

### DevOps & Infrastructure
- **Hosting**: 
  - Backend: AWS ECS/Fargate or Railway
  - Frontend: Vercel or Netlify
  - Database: Managed Neo4j Aura + AWS RDS
- **CI/CD**: GitHub Actions
- **Monitoring**: 
  - Application: Sentry
  - Infrastructure: CloudWatch/Datadog
- **Logging**: Structured logging with ELK stack

### Development Tools
- **Version Control**: Git + GitHub
- **API Documentation**: OpenAPI/Swagger
- **Testing**:
  - Backend: pytest
  - Frontend: Vitest + React Testing Library
- **Code Quality**: 
  - Python: black, ruff, mypy
  - TypeScript: ESLint, Prettier

---

## Data Model

### Neo4j Graph Schema
```
Nodes:
- Person (email, name, organization)
- Room (id, title, type)
- Message (id, text, timestamp, involvement)

Relationships:
- SENT (Person -> Message)
- IN_ROOM (Message -> Room)
- MENTIONED (Message -> Person)
- PARTICIPATES (Person -> Room)
```

### PostgreSQL Schema
```
Tables:
- users (id, email, name, google_id, created_at)
- subscriptions (id, user_id, status, expires_at, stripe_id)
- webex_credentials (id, user_id, encrypted_token, email)
- usage_logs (id, user_id, action, timestamp)
```

---

## API Endpoints (Planned)

### Authentication
- `POST /auth/google` - Google OAuth login
- `POST /auth/logout` - Logout
- `GET /auth/me` - Get current user

### Messages
- `POST /messages/fetch` - Fetch messages from Webex
- `GET /messages/graph` - Get graph data
- `POST /messages/query` - AI-powered search

### Subscription
- `POST /subscription/create` - Create Stripe checkout
- `GET /subscription/status` - Check subscription status
- `POST /subscription/cancel` - Cancel subscription

### Visualization
- `GET /graph/network` - Network graph data
- `GET /graph/timeline` - Timeline visualization data
- `GET /graph/stats` - Message statistics

---

## Security Considerations

1. **Credential Storage**: Encrypt Webex tokens at rest (AES-256)
2. **API Keys**: Store in environment variables, never commit
3. **Rate Limiting**: Prevent API abuse
4. **Data Privacy**: GDPR compliance, user data deletion
5. **SSL/TLS**: All traffic encrypted
6. **Input Validation**: Sanitize all user inputs
7. **CORS**: Restrict to known origins

---

## Cost Estimates (Monthly)

### Free Tier (100 users)
- Neo4j Aura: $65
- AWS RDS (PostgreSQL): $15
- AWS ECS: $30
- Vercel: $0 (hobby)
- OpenAI API: ~$50
- **Total**: ~$160/month

### Paid Tier (1000 users @ $12/year)
- Revenue: $1000/month
- Infrastructure: ~$300/month
- **Profit**: ~$700/month

---

## Development Phases

### Phase 1: Local Visualization (Week 1-2) ✅ COMPLETE
- [x] Message fetching script
- [x] Parse messages into graph format
- [x] Create local graph visualization (interactive HTML)
- [x] Static graph visualization (PNG)
- [x] Basic filtering and search
- [x] Date range filtering
- [x] Export graph data to JSON

### Phase 2: Web MVP (Week 3-6)
- [ ] FastAPI backend setup
- [ ] React frontend setup
- [ ] Google OAuth integration
- [ ] Neo4j integration
- [ ] Basic graph visualization on web

### Phase 3: AI Integration (Week 7-8)
- [ ] OpenAI API integration
- [ ] Natural language query interface
- [ ] Message summarization

### Phase 4: Payment & Launch (Week 9-12)
- [ ] Stripe integration
- [ ] Subscription management
- [ ] Free vs paid tier logic
- [ ] Production deployment
- [ ] Marketing site

---

## Next Steps

1. Create local graph visualization script
2. Test with existing message data
3. Iterate on visualization design
4. Plan web application architecture
