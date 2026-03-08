import 'package:flutter/material.dart';

import '../models/pokemon.dart';

class PokemonCard extends StatelessWidget {
  const PokemonCard({
    super.key,
    required this.pokemon,
    required this.onTap,
    this.isSelected = false,
    this.enabled = true,
  });

  final Pokemon pokemon;
  final VoidCallback onTap;
  final bool isSelected;
  final bool enabled;

  static const _typeColors = <String, Color>{
    'normal': Color(0xFFA8A77A),
    'fire': Color(0xFFEE8130),
    'water': Color(0xFF6390F0),
    'electric': Color(0xFFF7D02C),
    'grass': Color(0xFF7AC74C),
    'ice': Color(0xFF96D9D6),
    'fighting': Color(0xFFC22E28),
    'poison': Color(0xFFA33EA1),
    'ground': Color(0xFFE2BF65),
    'flying': Color(0xFFA98FF3),
    'psychic': Color(0xFFF95587),
    'bug': Color(0xFFA6B91A),
    'rock': Color(0xFFB6A136),
    'ghost': Color(0xFF735797),
    'dragon': Color(0xFF6F35FC),
    'dark': Color(0xFF705746),
    'steel': Color(0xFFB7B7CE),
    'fairy': Color(0xFFD685AD),
  };

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: enabled ? onTap : null,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeInOut,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected
              ? theme.colorScheme.primaryContainer
              : theme.colorScheme.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected
                ? theme.colorScheme.primary
                : theme.colorScheme.outlineVariant,
            width: isSelected ? 3 : 1,
          ),
          boxShadow: [
            if (isSelected)
              BoxShadow(
                color: theme.colorScheme.primary.withAlpha(60),
                blurRadius: 16,
                spreadRadius: 2,
              ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.network(
              pokemon.spriteUrl,
              height: 96,
              width: 96,
              fit: BoxFit.contain,
              filterQuality: FilterQuality.none,
              errorBuilder: (_, __, ___) => const SizedBox(
                height: 96,
                width: 96,
                child: Icon(Icons.catching_pokemon, size: 48),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _capitalize(pokemon.name),
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              children: pokemon.types.map((type) {
                return Chip(
                  label: Text(
                    _capitalize(type),
                    style: const TextStyle(fontSize: 11, color: Colors.white),
                  ),
                  backgroundColor: _typeColors[type] ?? Colors.grey,
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  visualDensity: VisualDensity.compact,
                  padding: EdgeInsets.zero,
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  static String _capitalize(String s) =>
      s.isEmpty ? s : '${s[0].toUpperCase()}${s.substring(1)}';
}
