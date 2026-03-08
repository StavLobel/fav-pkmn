import 'pokemon.dart';

class HistoryEntry {
  const HistoryEntry({
    required this.id,
    required this.matchDate,
    required this.pokemon,
    required this.totalVotes,
    this.winner,
  });

  final int id;
  final String matchDate;
  final List<Pokemon> pokemon;
  final int totalVotes;
  final Pokemon? winner;

  factory HistoryEntry.fromJson(Map<String, dynamic> json) {
    return HistoryEntry(
      id: json['id'] as int,
      matchDate: json['match_date'] as String,
      pokemon: (json['pokemon'] as List)
          .map((p) => Pokemon.fromJson(p as Map<String, dynamic>))
          .toList(),
      totalVotes: json['total_votes'] as int,
      winner: json['winner'] != null
          ? Pokemon.fromJson(json['winner'] as Map<String, dynamic>)
          : null,
    );
  }
}
