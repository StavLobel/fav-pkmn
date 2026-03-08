import 'package:flutter/foundation.dart';

import '../models/matchup.dart';
import '../models/vote_result.dart';
import '../services/api_service.dart';

enum LoadingState { idle, loading, loaded, error }

class MatchupProvider extends ChangeNotifier {
  MatchupProvider({ApiService? apiService})
      : _api = apiService ?? ApiService();

  final ApiService _api;

  Matchup? _matchup;
  VoteResults? _results;
  LoadingState _state = LoadingState.idle;
  String? _errorMessage;
  int? _userPick;
  bool _isSubmitting = false;

  Matchup? get matchup => _matchup;
  VoteResults? get results => _results;
  LoadingState get state => _state;
  String? get errorMessage => _errorMessage;
  int? get userPick => _userPick;
  bool get hasVoted => _matchup?.hasVoted ?? false;
  bool get isSubmitting => _isSubmitting;

  Future<void> loadTodayMatchup() async {
    _state = LoadingState.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      _matchup = await _api.getTodayMatchup();
      if (_matchup!.hasVoted) {
        _results = _matchup!.results;
        _userPick = _matchup!.userPick;
      }
      _state = LoadingState.loaded;
    } on ApiException catch (e) {
      _state = LoadingState.error;
      _errorMessage = 'Failed to load matchup: ${e.statusCode}';
    } catch (e) {
      _state = LoadingState.error;
      _errorMessage = 'Failed to load matchup. Check your connection.';
    }

    notifyListeners();
  }

  Future<void> submitVote(int pokemonId) async {
    if (_matchup == null || _isSubmitting) return;

    _isSubmitting = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _results = await _api.submitVote(_matchup!.id, pokemonId);
      _userPick = pokemonId;
      _matchup = Matchup(
        id: _matchup!.id,
        matchDate: _matchup!.matchDate,
        pokemon: _matchup!.pokemon,
        hasVoted: true,
        userPick: pokemonId,
        results: _results,
      );
    } on ApiException catch (e) {
      if (e.statusCode == 409) {
        _errorMessage = 'You have already voted today!';
        await loadTodayMatchup();
        return;
      }
      _errorMessage = 'Failed to submit vote.';
    } catch (e) {
      _errorMessage = 'Failed to submit vote. Check your connection.';
    }

    _isSubmitting = false;
    notifyListeners();
  }
}
