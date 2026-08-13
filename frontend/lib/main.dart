import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import 'providers/matchup_provider.dart';
import 'providers/streak_provider.dart';
import 'providers/theme_provider.dart';
import 'screens/daily_challenge_screen.dart';
import 'screens/history_screen.dart';
import 'screens/privacy_policy_screen.dart';

void main() {
  runApp(const PokePickApp());
}

class PokePickApp extends StatelessWidget {
  const PokePickApp({super.key});

  static const _seedColor = Color(0xFFE94560);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => MatchupProvider()),
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => StreakProvider()),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, _) {
          return MaterialApp(
            title: 'PokePick',
            debugShowCheckedModeBanner: false,
            theme: ThemeData(
              colorScheme: ColorScheme.fromSeed(
                seedColor: _seedColor,
                brightness: Brightness.light,
              ),
              useMaterial3: true,
              textTheme: GoogleFonts.outfitTextTheme(
                ThemeData(brightness: Brightness.light).textTheme,
              ),
            ),
            darkTheme: ThemeData(
              colorScheme: ColorScheme.fromSeed(
                seedColor: _seedColor,
                brightness: Brightness.dark,
              ),
              useMaterial3: true,
              textTheme: GoogleFonts.outfitTextTheme(
                ThemeData(brightness: Brightness.dark).textTheme,
              ),
            ),
            themeMode: themeProvider.themeMode,
            initialRoute: '/',
            onGenerateRoute: (settings) {
              final Widget page;
              switch (settings.name) {
                case '/history':
                  page = const HistoryScreen();
                case '/privacy':
                  page = const PrivacyPolicyScreen();
                default:
                  page = const DailyChallengeScreen();
              }
              return PageRouteBuilder(
                settings: settings,
                pageBuilder: (_, __, ___) => page,
                transitionsBuilder: (_, animation, __, child) {
                  return FadeTransition(
                    opacity: CurvedAnimation(
                        parent: animation, curve: Curves.easeOut),
                    child: child,
                  );
                },
                transitionDuration: const Duration(milliseconds: 250),
              );
            },
          );
        },
      ),
    );
  }
}
