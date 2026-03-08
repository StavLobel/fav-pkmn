class Pokemon {
  const Pokemon({
    required this.pokemonId,
    required this.name,
    required this.spriteUrl,
    required this.types,
  });

  final int pokemonId;
  final String name;
  final String spriteUrl;
  final List<String> types;

  factory Pokemon.fromJson(Map<String, dynamic> json) {
    return Pokemon(
      pokemonId: json['pokemon_id'] as int,
      name: json['name'] as String,
      spriteUrl: json['sprite_url'] as String,
      types: (json['types'] as List).cast<String>(),
    );
  }
}
