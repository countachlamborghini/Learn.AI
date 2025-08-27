import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/app.dart';
import 'core/di/injection.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive
  await Hive.initFlutter();
  
  // Initialize SharedPreferences
  await SharedPreferences.getInstance();
  
  // Initialize dependency injection
  await setupDependencyInjection();
  
  runApp(
    const ProviderScope(
      child: GlobalBrainApp(),
    ),
  );
}