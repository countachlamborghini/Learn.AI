import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:global_brain_student/app.dart';
import 'package:global_brain_student/config/theme.dart';
import 'package:global_brain_student/services/storage_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize services
  await StorageService.initialize();
  
  runApp(
    const ProviderScope(
      child: GlobalBrainApp(),
    ),
  );
}

class GlobalBrainApp extends ConsumerWidget {
  const GlobalBrainApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      title: 'Global Brain Student',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: const App(),
    );
  }
}