import 'package:flutter/material.dart';

import '../models/history_entry.dart';
import '../services/api_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final ApiService _api = ApiService();
  final List<HistoryEntry> _entries = [];
  bool _isLoading = false;
  bool _hasMore = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadMore();
  }

  Future<void> _loadMore() async {
    if (_isLoading || !_hasMore) return;
    setState(() => _isLoading = true);

    try {
      final newEntries = await _api.getHistory(
        limit: 20,
        offset: _entries.length,
      );
      setState(() {
        _entries.addAll(newEntries);
        _hasMore = newEntries.length == 20;
        _isLoading = false;
        _error = null;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'Failed to load history';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('History'),
        centerTitle: true,
      ),
      body: _error != null && _entries.isEmpty
          ? Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(_error!, style: theme.textTheme.bodyLarge),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: _loadMore,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Retry'),
                  ),
                ],
              ),
            )
          : _entries.isEmpty && _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _entries.isEmpty
                  ? Center(
                      child: Text(
                        'No history yet.\nCome back tomorrow!',
                        textAlign: TextAlign.center,
                        style: theme.textTheme.bodyLarge,
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _entries.length + (_hasMore ? 1 : 0),
                      itemBuilder: (context, index) {
                        if (index == _entries.length) {
                          _loadMore();
                          return const Padding(
                            padding: EdgeInsets.all(16),
                            child: Center(child: CircularProgressIndicator()),
                          );
                        }
                        return _HistoryCard(entry: _entries[index]);
                      },
                    ),
    );
  }
}

class _HistoryCard extends StatelessWidget {
  const _HistoryCard({required this.entry});

  final HistoryEntry entry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  entry.matchDate,
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                Text(
                  '${entry.totalVotes} vote${entry.totalVotes == 1 ? '' : 's'}',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: entry.pokemon.map((p) {
                final isWinner =
                    entry.winner != null && p.pokemonId == entry.winner!.pokemonId;
                return Column(
                  children: [
                    Stack(
                      clipBehavior: Clip.none,
                      children: [
                        Container(
                          decoration: isWinner
                              ? BoxDecoration(
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: const Color(0xFFFFD700),
                                    width: 2,
                                  ),
                                )
                              : null,
                          child: Padding(
                            padding: const EdgeInsets.all(4),
                            child: Image.network(
                              p.spriteUrl,
                              height: 48,
                              width: 48,
                              filterQuality: FilterQuality.none,
                              errorBuilder: (_, __, ___) => const SizedBox(
                                height: 48,
                                width: 48,
                                child: Icon(Icons.catching_pokemon, size: 24),
                              ),
                            ),
                          ),
                        ),
                        if (isWinner)
                          const Positioned(
                            top: -10,
                            right: -4,
                            child: Text('👑', style: TextStyle(fontSize: 14)),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _capitalize(p.name),
                      style: theme.textTheme.bodySmall?.copyWith(
                        fontWeight: isWinner ? FontWeight.bold : null,
                      ),
                    ),
                  ],
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
