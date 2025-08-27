# Global Brain Student Edition - Mobile App

Flutter mobile application for the Global Brain Student Edition platform.

## Setup Instructions

### Prerequisites
1. Install Flutter SDK (https://flutter.dev/docs/get-started/install)
2. Install Android Studio or VS Code with Flutter extensions
3. Set up Android/iOS development environment

### Installation
```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd mobile-app

# Install dependencies
flutter pub get

# Run the app
flutter run
```

### Project Structure
```
lib/
├── main.dart                 # App entry point
├── app.dart                  # Main app widget
├── config/
│   ├── api_config.dart       # API configuration
│   └── theme.dart           # App theme configuration
├── models/
│   ├── user.dart            # User model
│   ├── document.dart        # Document model
│   ├── session.dart         # Session model
│   └── progress.dart        # Progress model
├── services/
│   ├── auth_service.dart    # Authentication service
│   ├── api_service.dart     # API communication
│   └── storage_service.dart # Local storage
├── screens/
│   ├── auth/
│   │   ├── login_screen.dart
│   │   └── signup_screen.dart
│   ├── dashboard/
│   │   ├── dashboard_screen.dart
│   │   ├── upload_screen.dart
│   │   ├── tutor_screen.dart
│   │   ├── brain_boost_screen.dart
│   │   └── progress_screen.dart
│   └── common/
│       ├── loading_screen.dart
│       └── error_screen.dart
├── widgets/
│   ├── common/
│   │   ├── custom_button.dart
│   │   ├── custom_text_field.dart
│   │   └── progress_card.dart
│   └── dashboard/
│       ├── quick_action_card.dart
│       ├── progress_overview.dart
│       └── document_list.dart
└── utils/
    ├── constants.dart        # App constants
    └── helpers.dart         # Helper functions
```

## Features

### Core Features
1. **Authentication**
   - Login/Signup with email and password
   - JWT token management
   - Secure local storage

2. **Document Management**
   - Upload PDFs, DOCX, PPTX files
   - View document processing status
   - Access generated flashcards

3. **AI Tutor Chat**
   - Real-time chat with AI tutor
   - Level-adaptive responses
   - Source citations
   - Chat history

4. **Brain Boost Sessions**
   - 10-minute review sessions
   - Adaptive quiz questions
   - Progress tracking
   - Streak maintenance

5. **Progress Dashboard**
   - Mastery scores
   - Study streaks
   - Time saved metrics
   - Weak area identification

### Technical Features
- **State Management**: Provider/Riverpod
- **HTTP Client**: Dio for API communication
- **Local Storage**: SharedPreferences
- **File Upload**: Multipart requests
- **Real-time Updates**: WebSocket support
- **Offline Support**: Local caching

## API Integration

The mobile app communicates with the same backend API as the web application:

- **Base URL**: `http://localhost:8000` (development)
- **Authentication**: JWT Bearer tokens
- **File Upload**: Multipart form data
- **Real-time**: WebSocket for chat updates

## Development

### Running in Development Mode
```bash
flutter run --debug
```

### Building for Production
```bash
# Android
flutter build apk --release

# iOS
flutter build ios --release
```

### Testing
```bash
flutter test
```

## Dependencies

Key dependencies include:
- `dio`: HTTP client
- `provider`: State management
- `shared_preferences`: Local storage
- `file_picker`: File selection
- `flutter_secure_storage`: Secure storage
- `web_socket_channel`: Real-time communication

## Platform Support

- **Android**: API level 21+ (Android 5.0+)
- **iOS**: iOS 12.0+
- **Web**: Flutter web support (optional)

## Contributing

1. Follow Flutter coding conventions
2. Use meaningful commit messages
3. Test on both Android and iOS
4. Update documentation for new features