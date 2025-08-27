import 'package:flutter/material.dart';

void main() {
  runApp(const GlobalBrainApp());
}

class GlobalBrainApp extends StatelessWidget {
  const GlobalBrainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Global Brain',
      theme: ThemeData(primarySwatch: Colors.indigo),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final pages = <Widget>[
      _HomeCard(
        title: "Today’s Brain Boost",
        subtitle: "10 minutes — personalized review",
      ),
      _HomeCard(
        title: "Tutor Chat",
        subtitle: "Ask anything with sources",
      ),
      _HomeCard(
        title: "Documents",
        subtitle: "Upload and view flashcards",
      ),
      _HomeCard(
        title: "Dashboard",
        subtitle: "Mastery, weak spots, streaks",
      ),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Global Brain')),
      body: Center(child: pages[_selectedIndex]),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: (i) => setState(() => _selectedIndex = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.bolt), label: 'Boost'),
          BottomNavigationBarItem(icon: Icon(Icons.chat), label: 'Tutor'),
          BottomNavigationBarItem(icon: Icon(Icons.file_present), label: 'Docs'),
          BottomNavigationBarItem(icon: Icon(Icons.insights), label: 'Dashboard'),
        ],
      ),
    );
  }
}

class _HomeCard extends StatelessWidget {
  final String title;
  final String subtitle;
  const _HomeCard({required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(subtitle),
            const SizedBox(height: 12),
            FilledButton(onPressed: () {}, child: const Text('Open')),
          ],
        ),
      ),
    );
  }
}

