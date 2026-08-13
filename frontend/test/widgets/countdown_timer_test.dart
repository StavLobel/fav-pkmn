import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:poke_pick/widgets/countdown_timer.dart';

void main() {
  group('CountdownTimer', () {
    testWidgets('displays time in HH:MM:SS format', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: CountdownTimer()),
        ),
      );

      final text = find.textContaining(RegExp(r'\d{2}:\d{2}:\d{2}'));
      expect(text, findsOneWidget);
    });

    testWidgets('displays "Next challenge in" label', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: CountdownTimer()),
        ),
      );

      expect(find.text('Next challenge in'), findsOneWidget);
    });
  });
}
