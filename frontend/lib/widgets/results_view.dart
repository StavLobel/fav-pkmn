import 'package:flutter/material.dart';

import '../models/vote_result.dart';

class ResultsView extends StatelessWidget {
  const ResultsView({
    super.key,
    required this.results,
    this.userPick,
  });

  final VoteResults results;
  final int? userPick;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
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
      ],
    );
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

    return Padding(
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
                    child: Text('👑', style: TextStyle(fontSize: 20)),
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
                        _capitalize(result.name),
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
                    child: LinearProgressIndicator(
                      value: result.votePercentage / 100,
                      minHeight: 8,
                      backgroundColor: theme.colorScheme.surfaceContainerHighest,
                      valueColor: AlwaysStoppedAnimation(
                        result.isWinner
                            ? const Color(0xFFFFD700)
                            : theme.colorScheme.primary,
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
    );
  }

  static String _capitalize(String s) =>
      s.isEmpty ? s : '${s[0].toUpperCase()}${s.substring(1)}';
}
