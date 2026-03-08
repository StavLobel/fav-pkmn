import 'package:confetti/confetti.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/matchup_provider.dart';
import '../providers/streak_provider.dart';
import '../providers/theme_provider.dart';
import '../widgets/app_footer.dart';
import '../widgets/results_view.dart';
import '../widgets/voting_view.dart';

class DailyChallengeScreen extends StatefulWidget {
  const DailyChallengeScreen({super.key});

  @override
  State<DailyChallengeScreen> createState() => _DailyChallengeScreenState();
}

class _DailyChallengeScreenState extends State<DailyChallengeScreen> {
  late final ConfettiController _confettiController;
  bool _confettiFired = false;

  @override
  void initState() {
    super.initState();
    _confettiController =
        ConfettiController(duration: const Duration(seconds: 2));
    Future.microtask(
      () => context.read<MatchupProvider>().loadTodayMatchup(),
    );
  }

  @override
  void dispose() {
    _confettiController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MatchupProvider>();
    final themeProvider = context.watch<ThemeProvider>();
    final streakProvider = context.watch<StreakProvider>();
    final theme = Theme.of(context);

    if (provider.justVoted && !_confettiFired) {
      _confettiFired = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _confettiController.play();
        streakProvider.recordVote();
      });
    }

    final pageTitle = provider.hasVoted ? 'PokePick - Results' : 'PokePick - Vote Now';

    return Title(
      title: pageTitle,
      color: theme.colorScheme.primary,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('PokePick'),
          centerTitle: true,
          actions: [
            if (streakProvider.streak > 0)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.local_fire_department,
                        color: Color(0xFFFF6B35), size: 20),
                    const SizedBox(width: 2),
                    Text('${streakProvider.streak}',
                        style: theme.textTheme.bodyMedium),
                  ],
                ),
              ),
            IconButton(
              icon: Icon(themeProvider.isDark
                  ? Icons.light_mode
                  : Icons.dark_mode),
              tooltip: 'Toggle theme',
              onPressed: themeProvider.toggleTheme,
            ),
            IconButton(
              icon: const Icon(Icons.history),
              tooltip: 'History',
              onPressed: () => Navigator.pushNamed(context, '/history'),
            ),
          ],
        ),
        body: SafeArea(
          child: Stack(
            children: [
              _buildBody(provider, theme),
              Align(
                alignment: Alignment.topCenter,
                child: ConfettiWidget(
                  confettiController: _confettiController,
                  blastDirectionality: BlastDirectionality.explosive,
                  colors: const [
                    Color(0xFFE94560),
                    Color(0xFFFFD700),
                    Color(0xFF6390F0),
                    Color(0xFF7AC74C),
                  ],
                  numberOfParticles: 20,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBody(MatchupProvider provider, ThemeData theme) {
    switch (provider.state) {
      case LoadingState.idle:
      case LoadingState.loading:
        return const Center(child: CircularProgressIndicator());

      case LoadingState.error:
        return Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.cloud_off,
                  size: 64, color: theme.colorScheme.onSurfaceVariant),
              const SizedBox(height: 16),
              Text(
                provider.errorMessage ?? 'Something went wrong',
                style: theme.textTheme.bodyLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: provider.loadTodayMatchup,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        );

      case LoadingState.loaded:
        final matchup = provider.matchup!;

        if (provider.errorMessage != null) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(provider.errorMessage!)),
            );
          });
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 900),
              child: Column(
                children: [
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 400),
                    switchInCurve: Curves.easeOut,
                    switchOutCurve: Curves.easeIn,
                    child: provider.hasVoted
                        ? ResultsView(
                            key: const ValueKey('results'),
                            results: provider.results!,
                            userPick: provider.userPick,
                            justVoted: provider.justVoted,
                          )
                        : VotingView(
                            key: const ValueKey('voting'),
                            pokemon: matchup.pokemon,
                          ),
                  ),
                  const SizedBox(height: 32),
                  const AppFooter(),
                ],
              ),
            ),
          ),
        );
    }
  }
}
