import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:poke_pick/widgets/app_footer.dart';

void main() {
  group('AppFooter', () {
    testWidgets('renders disclaimer text', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: SingleChildScrollView(child: AppFooter())),
        ),
      );

      expect(find.textContaining('not affiliated with'), findsOneWidget);
      expect(find.textContaining('Nintendo'), findsOneWidget);
    });

    testWidgets('renders Privacy Policy link', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: SingleChildScrollView(child: AppFooter())),
        ),
      );

      expect(find.text('Privacy Policy'), findsOneWidget);
    });
  });
}
