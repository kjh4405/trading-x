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

// 로그인 및 대시보드 UI는 이전과 동일하게 유지됩니다.
// (생략된 세부 UI 코드는 요청 시 언제든 다시 전체 제공해 드릴 수 있습니다.)# trading-x
