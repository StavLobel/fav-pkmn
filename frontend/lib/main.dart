import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/matchup_provider.dart';
import 'screens/daily_challenge_screen.dart';
import 'screens/history_screen.dart';

void main() {
  runApp(const DailyStarterApp());
}

class DailyStarterApp extends StatelessWidget {
  const DailyStarterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => MatchupProvider(),
      child: MaterialApp(
        title: 'Daily Starter',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFFE94560),
            brightness: Brightness.dark,
          ),
          useMaterial3: true,
          fontFamily: 'Roboto',
        ),
        initialRoute: '/',
        routes: {
          '/': (_) => const DailyChallengeScreen(),
          '/history': (_) => const HistoryScreen(),
        },
      ),
    );
  }
}
