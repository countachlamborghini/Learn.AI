# Global Brain - Student Edition MVP

## Project Structure

```
global-brain/
├── backend/                     # FastAPI backend services
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # Database connection
│   │   ├── models/             # SQLAlchemy models
│   │   ├── api/                # API routes
│   │   ├── services/           # Business logic
│   │   ├── auth/               # Authentication
│   │   └── utils/              # Utilities
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/                    # React/Next.js web app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── styles/
│   ├── package.json
│   └── next.config.js
├── mobile/                      # Flutter mobile app
│   ├── lib/
│   │   ├── main.dart
│   │   ├── models/
│   │   ├── services/
│   │   ├── screens/
│   │   └── widgets/
│   ├── pubspec.yaml
│   └── android/
├── shared/                      # Shared configurations
│   ├── docker-compose.yml      # Full stack setup
│   └── k8s/                    # Kubernetes manifests
└── docs/                       # Documentation
    ├── api.md
    └── deployment.md
```