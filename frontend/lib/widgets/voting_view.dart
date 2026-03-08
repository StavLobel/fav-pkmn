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
        Text(
          'Who\'s your favorite?',
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
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
            if (constraints.maxWidth > 700) {
              return Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: pokemon
                    .map((p) => Expanded(
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 8),
                            child: PokemonCard(
                              pokemon: p,
                              enabled: !provider.isSubmitting,
                              onTap: () => provider.submitVote(p.pokemonId),
                            ),
                          ),
                        ))
                    .toList(),
              );
            }
            return Column(
              children: pokemon
                  .map((p) => Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: SizedBox(
                          width: double.infinity,
                          child: PokemonCard(
                            pokemon: p,
                            enabled: !provider.isSubmitting,
                            onTap: () => provider.submitVote(p.pokemonId),
                          ),
                        ),
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
