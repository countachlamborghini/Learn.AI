# Global Brain — Student Edition

Your AI study partner that organizes notes, tutors you at your level, and tracks progress — in minutes a day.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.9+
- Docker & Docker Compose
- Flutter SDK (for mobile app)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
docker-compose up -d  # Starts Postgres, Redis, Vector DB
python main.py
```

### Web App Setup
```bash
cd web-app
npm install
npm run dev
```

### Mobile App Setup
```bash
cd mobile-app
flutter pub get
flutter run
```

## 🏗️ Architecture

### Backend Services
- **API Gateway**: FastAPI with authentication & rate limiting
- **RAG Service**: Document processing, embeddings, retrieval
- **LLM Orchestrator**: AI model routing & tool calling
- **Content Services**: Flashcard & quiz generation
- **Auth Service**: Multi-tenant authentication & RBAC

### Data Stores
- **PostgreSQL**: User data, progress, billing
- **Vector DB**: Document embeddings & semantic search
- **Redis**: Caching & job queues
- **S3**: Document storage

### Frontend
- **Web**: React + Next.js with TypeScript
- **Mobile**: Flutter with Dart

## 📱 Core Features

1. **Smart Note Organizer**: Upload PDFs, slides, notes → auto-generate flashcards
2. **Adaptive Tutor Chat**: Level-adaptive AI tutor with source citations
3. **Daily Brain Boost**: 10-minute personalized review sessions
4. **Progress Dashboard**: Track mastery, streaks, and weak areas

## 🔧 Development

See individual README files in each directory for detailed setup instructions.

## 📊 Analytics & KPIs

- Weekly retention target: ≥40%
- NPS target: ≥30
- Score improvement: ≥15% after 2 weeks