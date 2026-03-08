import 'package:flutter_test/flutter_test.dart';
import 'package:daily_starter/main.dart';

void main() {
  testWidgets('App renders without crashing', (tester) async {
    await tester.pumpWidget(const DailyStarterApp());
    expect(find.text('Daily Challenge'), findsOneWidget);
  });
}
