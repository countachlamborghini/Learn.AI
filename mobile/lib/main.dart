import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'providers/auth_provider.dart';
import 'providers/document_provider.dart';
import 'providers/quiz_provider.dart';
import 'providers/progress_provider.dart';
import 'screens/splash_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/signup_screen.dart';
import 'screens/dashboard/dashboard_screen.dart';
import 'screens/documents/documents_screen.dart';
import 'screens/tutor/tutor_screen.dart';
import 'screens/quiz/brain_boost_screen.dart';
import 'screens/progress/progress_screen.dart';
import 'screens/profile/profile_screen.dart';
import 'utils/theme.dart';
import 'utils/constants.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive
  await Hive.initFlutter();
  
  runApp(const GlobalBrainApp());
}

class GlobalBrainApp extends StatelessWidget {
  const GlobalBrainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => DocumentProvider()),
        ChangeNotifierProvider(create: (_) => QuizProvider()),
        ChangeNotifierProvider(create: (_) => ProgressProvider()),
      ],
      child: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return MaterialApp.router(
            title: 'Global Brain',
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: ThemeMode.system,
            routerConfig: _createRouter(authProvider),
            debugShowCheckedModeBanner: false,
          );
        },
      ),
    );
  }

  GoRouter _createRouter(AuthProvider authProvider) {
    return GoRouter(
      initialLocation: '/',
      redirect: (context, state) {
        final isLoggedIn = authProvider.isAuthenticated;
        final isAuthRoute = state.matchedLocation == '/login' || 
                           state.matchedLocation == '/signup';

        if (!isLoggedIn && !isAuthRoute && state.matchedLocation != '/') {
          return '/login';
        }

        if (isLoggedIn && isAuthRoute) {
          return '/dashboard';
        }

        return null;
      },
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => const SplashScreen(),
        ),
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/signup',
          builder: (context, state) => const SignupScreen(),
        ),
        ShellRoute(
          builder: (context, state, child) => MainLayout(child: child),
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
              path: '/tutor',
              builder: (context, state) => const TutorScreen(),
            ),
            GoRoute(
              path: '/brain-boost',
              builder: (context, state) => const BrainBoostScreen(),
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
  }
}

class MainLayout extends StatelessWidget {
  final Widget child;

  const MainLayout({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _getCurrentIndex(context),
        onTap: (index) => _onTabTapped(context, index),
        selectedItemColor: Theme.of(context).primaryColor,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.folder),
            label: 'Documents',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.chat),
            label: 'Tutor',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.quiz),
            label: 'Brain Boost',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.trending_up),
            label: 'Progress',
          ),
        ],
      ),
    );
  }

  int _getCurrentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    switch (location) {
      case '/dashboard':
        return 0;
      case '/documents':
        return 1;
      case '/tutor':
        return 2;
      case '/brain-boost':
        return 3;
      case '/progress':
        return 4;
      default:
        return 0;
    }
  }

  void _onTabTapped(BuildContext context, int index) {
    switch (index) {
      case 0:
        context.go('/dashboard');
        break;
      case 1:
        context.go('/documents');
        break;
      case 2:
        context.go('/tutor');
        break;
      case 3:
        context.go('/brain-boost');
        break;
      case 4:
        context.go('/progress');
        break;
    }
  }
}