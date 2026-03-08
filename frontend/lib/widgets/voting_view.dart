import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/pokemon.dart';
import '../providers/matchup_provider.dart';
import 'pokemon_card.dart';

class VotingView extends StatelessWidget {
  const VotingView({super.key, required this.pokemon});

  final List<Pokemon> pokemon;

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MatchupProvider>();
    final theme = Theme.of(context);

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Semantics(
          header: true,
          child: Text(
            'Who\'s your favorite?',
            style: theme.textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Tap a Pokemon to cast your vote',
          style: theme.textTheme.bodyLarge?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 32),
        LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth > 700;

            final cards = pokemon
                .map((p) => PokemonCard(
                      pokemon: p,
                      enabled: !provider.isSubmitting,
                      onTap: () => provider.submitVote(p.pokemonId),
                    ))
                .toList();

            if (isWide) {
              return Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: cards
                    .map((card) => Expanded(
                          child: Padding(
                            padding:
                                const EdgeInsets.symmetric(horizontal: 8),
                            child: card,
                          ),
                        ))
                    .toList(),
              );
            }
            return Wrap(
              alignment: WrapAlignment.center,
              spacing: 16,
              runSpacing: 8,
              children: cards
                  .map((card) => SizedBox(
                        width: constraints.maxWidth > 500
                            ? (constraints.maxWidth - 64) / 2
                            : double.infinity,
                        child: card,
                      ))
                  .toList(),
            );
          },
        ),
        if (provider.isSubmitting) ...[
          const SizedBox(height: 24),
          const CircularProgressIndicator(),
        ],
      ],
    );
  }
}
