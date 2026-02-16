import 'package:flutter/material.dart';

void main() => runApp(const TradingXApp());

class TradingXApp extends StatelessWidget {
  const TradingXApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0A0E21),
        primaryColor: const Color(0xFF00F0FF),
      ),
      home: const LoginScreen(),
    );
  }
}

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ElevatedButton(
          child: const Text('Login to Trading X'),
          onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const Dashboard())),
        ),
      ),
    );
  }
}

class Dashboard extends StatelessWidget {
  const Dashboard({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Trading X Dashboard')),
      body: const Center(child: Text('Welcome to Trading X')),
    );
  }
}
