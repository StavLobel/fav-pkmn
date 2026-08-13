import 'package:flutter_test/flutter_test.dart';
import 'package:poke_pick/main.dart';

void main() {
  testWidgets('App renders without crashing', (tester) async {
    await tester.pumpWidget(const PokePickApp());
    expect(find.text('PokePick'), findsOneWidget);
  });
}
