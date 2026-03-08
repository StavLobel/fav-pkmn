import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/matchup_provider.dart';
import '../widgets/results_view.dart';
import '../widgets/voting_view.dart';

class DailyChallengeScreen extends StatefulWidget {
  const DailyChallengeScreen({super.key});

  @override
  State<DailyChallengeScreen> createState() => _DailyChallengeScreenState();
}

class _DailyChallengeScreenState extends State<DailyChallengeScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => context.read<MatchupProvider>().loadTodayMatchup(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MatchupProvider>();
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Daily Starter'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'History',
            onPressed: () => Navigator.pushNamed(context, '/history'),
          ),
        ],
      ),
      body: SafeArea(
        child: _buildBody(provider, theme),
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
              Icon(Icons.error_outline, size: 48,
                  color: theme.colorScheme.error),
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
              child: provider.hasVoted
                  ? ResultsView(
                      results: provider.results!,
                      userPick: provider.userPick,
                    )
                  : VotingView(pokemon: matchup.pokemon),
            ),
          ),
        );
    }
  }
}
