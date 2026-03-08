import 'package:flutter/material.dart';

import '../models/pokemon.dart';
import '../utils/string_utils.dart';

class PokemonCard extends StatefulWidget {
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

  static const typeColors = <String, Color>{
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
  State<PokemonCard> createState() => _PokemonCardState();
}

class _PokemonCardState extends State<PokemonCard> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final pokemon = widget.pokemon;

    return Semantics(
      label: '${capitalize(pokemon.name)}, ${pokemon.types.join(' and ')} type. Tap to vote.',
      button: true,
      enabled: widget.enabled,
      child: AnimatedScale(
        scale: _isPressed ? 0.96 : 1.0,
        duration: const Duration(milliseconds: 100),
        child: Material(
          color: Colors.transparent,
          borderRadius: BorderRadius.circular(20),
          child: InkWell(
            borderRadius: BorderRadius.circular(20),
            onTap: widget.enabled ? widget.onTap : null,
            onTapDown: widget.enabled ? (_) => setState(() => _isPressed = true) : null,
            onTapUp: widget.enabled ? (_) => setState(() => _isPressed = false) : null,
            onTapCancel: widget.enabled ? () => setState(() => _isPressed = false) : null,
            hoverColor: theme.colorScheme.primary.withAlpha(20),
            splashColor: theme.colorScheme.primary.withAlpha(40),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              curve: Curves.easeInOut,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: widget.isSelected
                    ? theme.colorScheme.primaryContainer
                    : theme.colorScheme.surface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: widget.isSelected
                      ? theme.colorScheme.primary
                      : theme.colorScheme.outlineVariant,
                  width: widget.isSelected ? 3 : 1,
                ),
                boxShadow: [
                  if (widget.isSelected)
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
                    semanticLabel: '${pokemon.name} sprite',
                    loadingBuilder: (_, child, progress) {
                      if (progress == null) return child;
                      return const SizedBox(
                        height: 96,
                        width: 96,
                        child: Center(
                            child: CircularProgressIndicator(strokeWidth: 2)),
                      );
                    },
                    errorBuilder: (_, __, ___) => const SizedBox(
                      height: 96,
                      width: 96,
                      child: Icon(Icons.catching_pokemon, size: 48),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    capitalize(pokemon.name),
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
                          capitalize(type),
                          style: const TextStyle(fontSize: 11, color: Colors.white),
                        ),
                        backgroundColor: PokemonCard.typeColors[type] ?? Colors.grey,
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        visualDensity: VisualDensity.compact,
                        padding: EdgeInsets.zero,
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
