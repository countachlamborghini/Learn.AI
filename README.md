# Global Brain - Student Edition MVP

Your AI study partner that organizes notes, tutors you at your level, and tracks progress — in minutes a day.

## 🚀 Features

- **Smart Note Organizer**: Upload PDFs, DOCX, PPTX, and images. Auto-generates flashcards and summaries
- **Adaptive Tutor Chat**: AI-powered tutoring with source citations and adjustable reading levels
- **Daily Brain Boost**: 10-minute personalized review sessions with spaced repetition
- **Progress Dashboard**: Track topic mastery, streaks, and learning analytics
- **Multi-Platform**: Web app and mobile app (iOS/Android via Flutter)
- **Privacy-First**: COPPA/FERPA compliant with data isolation and export controls

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **API Gateway**: RESTful API with authentication and rate limiting
- **Document Processing**: OCR, parsing, chunking, and embedding generation
- **RAG System**: Vector search with Pinecone, retrieval and re-ranking
- **LLM Integration**: OpenAI GPT models with tool use and adaptive prompting
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for session storage and API caching
- **Storage**: AWS S3 for documents and artifacts

### Frontend (Next.js + React)
- **Modern UI**: Tailwind CSS with responsive design
- **Authentication**: JWT-based auth with automatic token refresh
- **Real-time**: WebSocket connections for live tutoring
- **File Upload**: Drag-and-drop with progress tracking
- **Responsive**: Mobile-first design principles

### Mobile (Flutter)
- **Cross-Platform**: iOS and Android from single codebase
- **Native Performance**: Optimized for mobile interaction patterns
- **Offline Support**: Local storage for flashcards and progress
- **Push Notifications**: Study reminders and achievement alerts

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Flutter 3.10+ (for mobile development)

### Environment Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd global-brain
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - PINECONE_API_KEY
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - STRIPE_API_KEY
```

3. **Start with Docker Compose**
```bash
cd shared
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis cache on port 6379
- FastAPI backend on port 8000
- Next.js frontend on port 3000
- Nginx reverse proxy on port 80

### Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

#### Mobile Development
```bash
cd mobile
flutter pub get
flutter run
```

## 📱 Mobile App Setup

### iOS
```bash
cd mobile
flutter run -d ios
```

### Android
```bash
cd mobile
flutter run -d android
```

### Build for Production
```bash
# iOS
flutter build ios --release

# Android
flutter build apk --release
flutter build appbundle --release
```

## 🔧 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /v1/auth/signup` - Create new user account
- `POST /v1/auth/login` - Authenticate user
- `GET /v1/auth/me` - Get current user info

#### Documents
- `POST /v1/docs/upload` - Upload document
- `GET /v1/docs/` - List user documents
- `POST /v1/docs/{id}/generate-flashcards` - Generate flashcards

#### Tutor
- `POST /v1/tutor/chat` - Chat with AI tutor
- `POST /v1/tutor/boost/start` - Start Brain Boost session
- `POST /v1/tutor/boost/answer` - Submit quiz answer

#### Progress
- `GET /v1/progress/overview` - Progress overview
- `GET /v1/progress/topics` - Topic mastery levels
- `GET /v1/progress/weak-areas` - Areas needing focus

## 🗄️ Database Schema

### Core Tables
- `users` - User accounts and profiles
- `tenants` - Organizations/schools (multi-tenant)
- `documents` - Uploaded files and metadata
- `doc_chunks` - Text chunks for RAG
- `embeddings` - Vector embeddings
- `flashcards` - Generated flashcards
- `sessions` - Learning sessions
- `messages` - Chat history
- `mastery` - Topic mastery tracking

## 🚀 Deployment

### Production Docker Setup
```bash
# Build and deploy
docker-compose -f shared/docker-compose.yml up -d

# Monitor logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Environment Variables (Production)
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/globalbrain

# Redis
REDIS_URL=redis://host:6379

# OpenAI
OPENAI_API_KEY=sk-...

# Pinecone
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=globalbrain-embeddings

# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-west-2
S3_BUCKET_NAME=globalbrain-documents

# Stripe
STRIPE_API_KEY=sk_live_...

# Security
SECRET_KEY=your-super-secure-secret-key
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### Kubernetes Deployment
```bash
cd shared/k8s
kubectl apply -f .
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Mobile Tests
```bash
cd mobile
flutter test
```

## 📊 Monitoring & Analytics

### Health Checks
- Backend: `GET /health`
- Database: Built-in PostgreSQL health checks
- Redis: Built-in Redis health checks

### Metrics
- Prometheus metrics exposed at `/metrics`
- Grafana dashboards for visualization
- Structured logging with correlation IDs

### Key Metrics
- User engagement (DAU/WAU)
- Brain Boost completion rates
- Document processing success rates
- API response times
- Cost per active user

## 🔒 Security & Privacy

### Data Protection
- End-to-end encryption for sensitive data
- PII encryption at rest
- TLS 1.3 for data in transit
- Tenant data isolation

### Compliance
- COPPA compliant (under-13 workflows)
- FERPA aware (no targeted ads, data minimization)
- GDPR ready (data export/deletion)

### Authentication
- JWT with automatic refresh
- Multi-factor authentication support
- Rate limiting and abuse protection

## 📈 Scaling Considerations

### Horizontal Scaling
- Stateless backend services
- Load balancer configuration
- Database read replicas
- Redis clustering

### Cost Optimization
- LLM token caching
- Batch processing for embeddings
- CDN for static assets
- Auto-scaling based on demand

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- Backend: Black + isort + flake8
- Frontend: Prettier + ESLint
- Mobile: Flutter's dart format

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Email**: support@globalbrain.ai
- **Discord**: [Global Brain Community](https://discord.gg/globalbrain)

## 🎯 Roadmap

### Phase 1 (MVP - Completed) ✅
- Document upload and processing
- AI tutor chat with RAG
- Basic flashcard generation
- Simple progress tracking
- Web and mobile apps

### Phase 2 (Next 3 months)
- Advanced spaced repetition
- Teacher dashboard
- Class management
- Real-time collaboration
- Advanced analytics

### Phase 3 (6 months)
- Voice interaction
- Handwriting recognition
- AR/VR integration
- Advanced AI models
- Enterprise features

---

Built with ❤️ for learners everywhere. Happy studying! 🧠✨