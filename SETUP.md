# Global Brain Student Edition - Complete Setup Guide

This guide will help you set up the entire Global Brain Student Edition platform, including the backend API, web application, and mobile app.

## 🏗️ Architecture Overview

```
Global Brain Student Edition
├── backend/           # FastAPI Python backend
├── web-app/          # Next.js React web application
└── mobile-app/       # Flutter mobile application
```

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows
- **Python**: 3.9+ 
- **Node.js**: 18+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Flutter**: 3.0+ (for mobile development)

### Development Tools
- **Code Editor**: VS Code, PyCharm, or similar
- **Git**: For version control
- **Postman/Insomnia**: For API testing

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd global-brain-student
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

#### Start Infrastructure Services
```bash
docker-compose up -d
```

#### Initialize Database
```bash
# The database will be automatically created when you start the app
python main.py
```

#### Start the Backend Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 3. Web Application Setup

#### Install Dependencies
```bash
cd web-app
npm install
```

#### Set Up Environment Variables
```bash
cp .env.example .env.local
# Edit .env.local with your API URL
```

#### Start Development Server
```bash
npm run dev
```

The web app will be available at: http://localhost:3000

### 4. Mobile Application Setup

#### Install Flutter
Follow the official Flutter installation guide: https://flutter.dev/docs/get-started/install

#### Install Dependencies
```bash
cd mobile-app
flutter pub get
```

#### Run the App
```bash
flutter run
```

## 🔧 Configuration

### Backend Configuration (.env)
```env
# App Settings
APP_NAME=Global Brain Student Edition
APP_VERSION=1.0.0
DEBUG=true

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/globalbrain

# Redis
REDIS_URL=redis://localhost:6379

# Vector DB
CHROMA_HOST=localhost
CHROMA_PORT=8000

# S3/MinIO
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=globalbrain-docs
S3_REGION=us-east-1

# AI/LLM
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### Web App Configuration (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🗄️ Database Schema

The application uses PostgreSQL with the following main tables:

- **users**: User accounts and authentication
- **tenants**: Multi-tenant support for schools/organizations
- **documents**: Uploaded study materials
- **doc_chunks**: Processed document chunks
- **embeddings**: Vector embeddings for semantic search
- **flashcards**: Generated flashcards
- **sessions**: Tutor chat and Brain Boost sessions
- **messages**: Chat messages with AI tutor
- **mastery**: Learning progress tracking

## 🔌 API Endpoints

### Authentication
- `POST /v1/auth/signup` - User registration
- `POST /v1/auth/login` - User login
- `GET /v1/auth/me` - Get current user

### Documents
- `POST /v1/docs/upload` - Upload document
- `GET /v1/docs/` - List documents
- `GET /v1/docs/{id}` - Get document details
- `GET /v1/docs/{id}/flashcards` - Get document flashcards

### Tutor
- `POST /v1/tutor/chat` - Chat with AI tutor
- `POST /v1/tutor/boost/start` - Start Brain Boost session
- `POST /v1/tutor/boost/answer` - Answer Brain Boost questions

### Progress
- `GET /v1/progress/overview` - Get progress overview
- `GET /v1/progress/topics` - Get topic mastery
- `GET /v1/progress/analytics` - Get learning analytics

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest
```

### Web App Testing
```bash
cd web-app
npm test
```

### Mobile App Testing
```bash
cd mobile-app
flutter test
```

## 🚀 Deployment

### Backend Deployment
1. Set up a production PostgreSQL database
2. Configure environment variables for production
3. Use a production WSGI server (Gunicorn)
4. Set up reverse proxy (Nginx)
5. Configure SSL certificates

### Web App Deployment
1. Build the production version: `npm run build`
2. Deploy to Vercel, Netlify, or your preferred hosting
3. Configure environment variables
4. Set up custom domain

### Mobile App Deployment
1. Build for Android: `flutter build apk --release`
2. Build for iOS: `flutter build ios --release`
3. Submit to app stores

## 🔒 Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **API Keys**: Use secure storage for API keys
3. **CORS**: Configure allowed origins properly
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Input Validation**: Validate all user inputs
6. **File Upload**: Scan uploaded files for malware
7. **HTTPS**: Use HTTPS in production

## 📊 Monitoring & Analytics

### Backend Monitoring
- Use OpenTelemetry for distributed tracing
- Set up Prometheus/Grafana for metrics
- Configure Sentry for error tracking

### Web App Analytics
- Google Analytics for user behavior
- Custom event tracking for learning metrics

### Mobile App Analytics
- Firebase Analytics for mobile usage
- Crash reporting with Firebase Crashlytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 Development Workflow

### Daily Development
1. Start infrastructure: `docker-compose up -d`
2. Start backend: `uvicorn main:app --reload`
3. Start web app: `npm run dev`
4. Run mobile app: `flutter run`

### Code Quality
- Use pre-commit hooks for formatting
- Run linting: `flake8` (Python), `npm run lint` (JavaScript)
- Follow coding standards for each language

## 🆘 Troubleshooting

### Common Issues

#### Backend Issues
- **Database connection**: Check if PostgreSQL is running
- **Redis connection**: Verify Redis is accessible
- **Vector DB**: Ensure ChromaDB is running on port 8000

#### Web App Issues
- **API connection**: Verify backend is running on port 8000
- **Build errors**: Clear node_modules and reinstall

#### Mobile App Issues
- **Flutter version**: Ensure Flutter 3.0+ is installed
- **Dependencies**: Run `flutter pub get` to update dependencies

### Getting Help
1. Check the logs for error messages
2. Verify all services are running
3. Check environment variable configuration
4. Consult the API documentation at `/docs`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Flutter Documentation](https://flutter.dev/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## 🎯 Next Steps

After setting up the development environment:

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test the Web App**: Navigate to http://localhost:3000
3. **Run the Mobile App**: Use `flutter run` in the mobile-app directory
4. **Upload a Document**: Test the document processing pipeline
5. **Try the AI Tutor**: Start a chat session
6. **Complete a Brain Boost**: Test the quiz functionality

## 📞 Support

For technical support or questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation
- Consult the development logs