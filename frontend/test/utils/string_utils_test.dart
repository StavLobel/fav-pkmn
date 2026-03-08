import 'package:flutter_test/flutter_test.dart';
import 'package:poke_pick/utils/string_utils.dart';

void main() {
  group('capitalize', () {
    test('returns empty string for empty input', () {
      expect(capitalize(''), '');
    });

    test('capitalizes single character', () {
      expect(capitalize('a'), 'A');
    });

    test('capitalizes first letter of a normal string', () {
      expect(capitalize('pikachu'), 'Pikachu');
    });

    test('preserves already capitalized string', () {
      expect(capitalize('Bulbasaur'), 'Bulbasaur');
    });

    test('only capitalizes first letter', () {
      expect(capitalize('chARmAnDeR'), 'ChARmAnDeR');
    });
  });
}
