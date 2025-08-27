import 'package:flutter/material.dart';

class BrainBoostScreen extends StatelessWidget {
  const BrainBoostScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Brain Boost'),
      ),
      body: const Center(
        child: Text('Brain Boost - Coming Soon'),
      ),
    );
  }
}