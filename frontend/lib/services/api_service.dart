import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../models/history_entry.dart';
import '../models/matchup.dart';
import '../models/vote_result.dart';

class ApiService {
  ApiService({String? baseUrl})
      : _baseUrl = baseUrl ?? _defaultBaseUrl;

  final String _baseUrl;

  static String get _defaultBaseUrl {
    if (kReleaseMode) {
      return '';
    }
    return 'http://localhost:8000';
  }

  Future<Matchup> getTodayMatchup() async {
    final response = await http.get(
      Uri.parse('$_baseUrl/api/matchup/today'),
    );
    _checkResponse(response);
    return Matchup.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<VoteResults> submitVote(int matchupId, int pokemonId) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/api/vote'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'matchup_id': matchupId,
        'pokemon_id': pokemonId,
      }),
    );
    _checkResponse(response);
    return VoteResults.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<List<HistoryEntry>> getHistory({int limit = 30, int offset = 0}) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/api/history?limit=$limit&offset=$offset'),
    );
    _checkResponse(response);
    final list = jsonDecode(response.body) as List;
    return list
        .map((e) => HistoryEntry.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  void _checkResponse(http.Response response) {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode, response.body);
    }
  }
}

class ApiException implements Exception {
  const ApiException(this.statusCode, this.body);

  final int statusCode;
  final String body;

  @override
  String toString() => 'ApiException($statusCode): $body';
}
