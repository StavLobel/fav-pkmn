import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:poke_pick/screens/privacy_policy_screen.dart';

void main() {
  group('PrivacyPolicyScreen', () {
    testWidgets('renders Privacy Policy title in app bar', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: PrivacyPolicyScreen()),
      );

      expect(find.text('Privacy Policy'), findsOneWidget);
    });

    testWidgets('contains cookies section', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: PrivacyPolicyScreen()),
      );

      expect(find.textContaining('Cookies'), findsWidgets);
    });

    testWidgets('contains what we collect section', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: PrivacyPolicyScreen()),
      );

      expect(find.textContaining('What We Collect'), findsWidgets);
    });

    testWidgets('contains third-party services section', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: PrivacyPolicyScreen()),
      );

      expect(find.textContaining('Third-Party Services'), findsWidgets);
    });

    testWidgets('mentions PokeAPI', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: PrivacyPolicyScreen()),
      );

      expect(find.textContaining('PokeAPI'), findsWidgets);
    });
  });
}
