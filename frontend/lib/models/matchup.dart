import 'pokemon.dart';
import 'vote_result.dart';

class Matchup {
  const Matchup({
    required this.id,
    required this.matchDate,
    required this.pokemon,
    required this.hasVoted,
    this.userPick,
    this.results,
  });

  final int id;
  final String matchDate;
  final List<Pokemon> pokemon;
  final bool hasVoted;
  final int? userPick;
  final VoteResults? results;

  factory Matchup.fromJson(Map<String, dynamic> json) {
    return Matchup(
      id: json['id'] as int,
      matchDate: json['match_date'] as String,
      pokemon: (json['pokemon'] as List)
          .map((p) => Pokemon.fromJson(p as Map<String, dynamic>))
          .toList(),
      hasVoted: json['has_voted'] as bool,
      userPick: json['user_pick'] as int?,
      results: json['results'] != null
          ? VoteResults.fromJson(json['results'] as Map<String, dynamic>)
          : null,
    );
  }
}
