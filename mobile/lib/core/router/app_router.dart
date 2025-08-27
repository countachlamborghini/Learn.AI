import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/providers/auth_provider.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/signup_screen.dart';
import '../../features/onboarding/screens/onboarding_screen.dart';
import '../../features/dashboard/screens/dashboard_screen.dart';
import '../../features/documents/screens/documents_screen.dart';
import '../../features/documents/screens/upload_screen.dart';
import '../../features/tutor/screens/tutor_chat_screen.dart';
import '../../features/brain_boost/screens/brain_boost_screen.dart';
import '../../features/flashcards/screens/flashcards_screen.dart';
import '../../features/progress/screens/progress_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../widgets/main_navigation.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);
  
  return GoRouter(
    initialLocation: '/onboarding',
    redirect: (context, state) {
      final isAuthenticated = authState.isAuthenticated;
      final isOnboarding = state.location == '/onboarding';
      final isAuth = state.location.startsWith('/auth');
      
      // If not authenticated and not on auth or onboarding screens, redirect to login
      if (!isAuthenticated && !isAuth && !isOnboarding) {
        return '/auth/login';
      }
      
      // If authenticated and on auth screens, redirect to dashboard
      if (isAuthenticated && (isAuth || isOnboarding)) {
        return '/dashboard';
      }
      
      return null;
    },
    routes: [
      // Onboarding
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      
      // Authentication
      GoRoute(
        path: '/auth/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/auth/signup',
        builder: (context, state) => const SignupScreen(),
      ),
      
      // Main Shell with Bottom Navigation
      ShellRoute(
        builder: (context, state, child) => MainNavigation(child: child),
        routes: [
          GoRoute(
            path: '/dashboard',
            builder: (context, state) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/documents',
            builder: (context, state) => const DocumentsScreen(),
          ),
          GoRoute(
            path: '/upload',
            builder: (context, state) => const UploadScreen(),
          ),
          GoRoute(
            path: '/tutor',
            builder: (context, state) => const TutorChatScreen(),
          ),
          GoRoute(
            path: '/brain-boost',
            builder: (context, state) => const BrainBoostScreen(),
          ),
          GoRoute(
            path: '/flashcards',
            builder: (context, state) => const FlashcardsScreen(),
          ),
          GoRoute(
            path: '/progress',
            builder: (context, state) => const ProgressScreen(),
          ),
          GoRoute(
            path: '/profile',
            builder: (context, state) => const ProfileScreen(),
          ),
        ],
      ),
    ],
  );
});