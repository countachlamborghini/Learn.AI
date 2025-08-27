# Global Brain — Student Edition (MVP)

Your AI study partner that organizes notes, tutors you at your level, and tracks progress — in minutes a day.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Docker and Docker Compose
- Flutter SDK (for mobile app)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Mobile App Setup
```bash
cd mobile
flutter pub get
flutter run
```

## 🏗️ Architecture

### Backend Services
- **API Gateway**: FastAPI with authentication and rate limiting
- **RAG Service**: Document processing, embeddings, and retrieval
- **AI Orchestrator**: LLM integration with tool calling
- **Content Services**: Flashcard and quiz generation
- **Auth Service**: Multi-tenant authentication and authorization

### Data Stores
- **PostgreSQL**: User data, progress tracking, billing
- **Vector Database**: Document embeddings and semantic search
- **Redis**: Caching and session management
- **S3**: Document storage and artifacts

### Frontend
- **Web App**: React with Next.js for optimal performance
- **Mobile App**: Flutter for cross-platform mobile experience

## 📱 Core Features

1. **Smart Note Organizer**: Upload PDFs, slides, and notes with automatic processing
2. **Adaptive Tutor Chat**: AI-powered tutoring with source citations
3. **Daily Brain Boost**: 10-minute personalized review sessions
4. **Progress Dashboard**: Track mastery, streaks, and weak areas

## 🔧 Development

### Environment Variables
Create `.env` files in each service directory with:
- Database connections
- API keys (OpenAI, Pinecone, etc.)
- JWT secrets
- S3 credentials

### Testing
```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test

# Mobile tests
cd mobile && flutter test
```

## 📊 Analytics & Monitoring
- OpenTelemetry for distributed tracing
- Prometheus/Grafana for metrics
- Sentry for error tracking

## 🔒 Security & Privacy
- Multi-tenant data isolation
- COPPA/FERPA compliance
- PII encryption at rest
- User data export/deletion controls

## 📈 Success Metrics
- ≥40% weekly retention
- NPS ≥ 30
- ≥15% score improvement after 2 weeks

## 🚀 Deployment
- Docker containers for all services
- Kubernetes for orchestration
- CI/CD with GitHub Actions
- Multi-region support for compliance

---

Built with ❤️ for students worldwide