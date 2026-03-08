class PokemonResult {
  const PokemonResult({
    required this.pokemonId,
    required this.name,
    required this.spriteUrl,
    required this.types,
    required this.voteCount,
    required this.votePercentage,
    required this.isWinner,
  });

  final int pokemonId;
  final String name;
  final String spriteUrl;
  final List<String> types;
  final int voteCount;
  final double votePercentage;
  final bool isWinner;

  factory PokemonResult.fromJson(Map<String, dynamic> json) {
    return PokemonResult(
      pokemonId: json['pokemon_id'] as int,
      name: json['name'] as String,
      spriteUrl: json['sprite_url'] as String,
      types: (json['types'] as List).cast<String>(),
      voteCount: json['vote_count'] as int,
      votePercentage: (json['vote_percentage'] as num).toDouble(),
      isWinner: json['is_winner'] as bool,
    );
  }
}

class VoteResults {
  const VoteResults({
    required this.matchupId,
    required this.totalVotes,
    required this.pokemon,
  });

  final int matchupId;
  final int totalVotes;
  final List<PokemonResult> pokemon;

  factory VoteResults.fromJson(Map<String, dynamic> json) {
    return VoteResults(
      matchupId: json['matchup_id'] as int,
      totalVotes: json['total_votes'] as int,
      pokemon: (json['pokemon'] as List)
          .map((p) => PokemonResult.fromJson(p as Map<String, dynamic>))
          .toList(),
    );
  }
}
