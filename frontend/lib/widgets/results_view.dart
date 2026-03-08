import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/vote_result.dart';
import '../utils/string_utils.dart';
import 'countdown_timer.dart';

class ResultsView extends StatelessWidget {
  const ResultsView({
    super.key,
    required this.results,
    this.userPick,
    this.justVoted = false,
  });

  final VoteResults results;
  final int? userPick;
  final bool justVoted;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (!justVoted)
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: theme.colorScheme.tertiaryContainer,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                'You voted earlier today!',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onTertiaryContainer,
                ),
              ),
            ),
          ),
        Text(
          'Today\'s Results',
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          '${results.totalVotes} total vote${results.totalVotes == 1 ? '' : 's'}',
          style: theme.textTheme.bodyLarge?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 32),
        ...results.pokemon.map((p) => _ResultCard(
              result: p,
              isUserPick: p.pokemonId == userPick,
            )),
        const SizedBox(height: 24),
        FilledButton.icon(
          onPressed: () => _shareResults(context),
          icon: const Icon(Icons.share),
          label: const Text('Share'),
        ),
        const SizedBox(height: 32),
        const CountdownTimer(),
      ],
    );
  }

  Future<void> _shareResults(BuildContext context) async {
    final buffer = StringBuffer('PokePick\n\n');
    for (final p in results.pokemon) {
      final filled = (p.votePercentage / 10).round();
      final bar = '${'█' * filled}${'░' * (10 - filled)}';
      final pick = p.pokemonId == userPick ? '  <--' : '';
      buffer.writeln(
          '${capitalize(p.name).padRight(12)} $bar ${p.votePercentage.round()}%$pick');
    }
    await Clipboard.setData(ClipboardData(text: buffer.toString()));
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Results copied to clipboard!')),
      );
    }
  }
}

class _ResultCard extends StatelessWidget {
  const _ResultCard({
    required this.result,
    required this.isUserPick,
  });

  final PokemonResult result;
  final bool isUserPick;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Semantics(
      label: '${capitalize(result.name)}: ${result.voteCount} votes, '
          '${result.votePercentage.round()} percent. '
          '${result.isWinner ? "Winner." : ""} '
          '${isUserPick ? "Your pick." : ""}',
      child: Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isUserPick
                ? theme.colorScheme.primaryContainer
                : theme.colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: result.isWinner
                  ? const Color(0xFFFFD700)
                  : isUserPick
                      ? theme.colorScheme.primary
                      : theme.colorScheme.outlineVariant,
              width: result.isWinner ? 2 : 1,
            ),
          ),
          child: Row(
            children: [
              Stack(
                clipBehavior: Clip.none,
                children: [
                  Image.network(
                    result.spriteUrl,
                    height: 64,
                    width: 64,
                    fit: BoxFit.contain,
                    filterQuality: FilterQuality.none,
                    semanticLabel: '${result.name} sprite',
                    loadingBuilder: (_, child, progress) {
                      if (progress == null) return child;
                      return const SizedBox(
                        height: 64,
                        width: 64,
                        child: Center(
                            child: CircularProgressIndicator(strokeWidth: 2)),
                      );
                    },
                    errorBuilder: (_, __, ___) => const SizedBox(
                      height: 64,
                      width: 64,
                      child: Icon(Icons.catching_pokemon, size: 32),
                    ),
                  ),
                  if (result.isWinner)
                    const Positioned(
                      top: -8,
                      right: -8,
                      child: Icon(
                        Icons.workspace_premium,
                        color: Color(0xFFFFD700),
                        size: 24,
                        shadows: [Shadow(color: Colors.black54, blurRadius: 4)],
                      ),
                    ),
                ],
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          capitalize(result.name),
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        if (isUserPick) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: theme.colorScheme.primary,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              'Your pick',
                              style: TextStyle(
                                fontSize: 11,
                                color: theme.colorScheme.onPrimary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(6),
                      child: TweenAnimationBuilder<double>(
                        tween: Tween(begin: 0, end: result.votePercentage / 100),
                        duration: const Duration(milliseconds: 800),
                        curve: Curves.easeOutCubic,
                        builder: (context, value, _) => LinearProgressIndicator(
                          value: value,
                          minHeight: 8,
                          backgroundColor:
                              theme.colorScheme.surfaceContainerHighest,
                          valueColor: AlwaysStoppedAnimation(
                            result.isWinner
                                ? const Color(0xFFFFD700)
                                : theme.colorScheme.primary,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${result.voteCount} vote${result.voteCount == 1 ? '' : 's'} (${result.votePercentage}%)',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
