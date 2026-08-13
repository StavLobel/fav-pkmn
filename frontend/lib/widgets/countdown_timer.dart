import 'dart:async';

import 'package:flutter/material.dart';

class CountdownTimer extends StatefulWidget {
  const CountdownTimer({super.key, this.onComplete});

  final VoidCallback? onComplete;

  @override
  State<CountdownTimer> createState() => _CountdownTimerState();
}

class _CountdownTimerState extends State<CountdownTimer> {
  late Timer _timer;
  Duration _remaining = Duration.zero;

  @override
  void initState() {
    super.initState();
    _computeRemaining();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      _computeRemaining();
      if (_remaining <= Duration.zero) {
        _timer.cancel();
        widget.onComplete?.call();
      }
    });
  }

  void _computeRemaining() {
    final now = DateTime.now();
    final midnight = DateTime(now.year, now.month, now.day + 1);
    setState(() => _remaining = midnight.difference(now));
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final hours = _remaining.inHours.toString().padLeft(2, '0');
    final minutes = (_remaining.inMinutes % 60).toString().padLeft(2, '0');
    final seconds = (_remaining.inSeconds % 60).toString().padLeft(2, '0');

    return Column(
      children: [
        Text(
          'Next challenge in',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          '$hours:$minutes:$seconds',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
            fontFamily: 'monospace',
            letterSpacing: 2,
          ),
        ),
      ],
    );
  }
}
