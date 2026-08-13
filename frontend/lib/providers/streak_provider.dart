import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StreakProvider extends ChangeNotifier {
  StreakProvider() {
    _load();
  }

  int _streak = 0;

  int get streak => _streak;

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    _streak = prefs.getInt('streak') ?? 0;
    notifyListeners();
  }

  Future<void> recordVote() async {
    final prefs = await SharedPreferences.getInstance();
    final lastDate = prefs.getString('last_vote_date');
    final streak = prefs.getInt('streak') ?? 0;
    final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
    final yesterday = DateFormat('yyyy-MM-dd')
        .format(DateTime.now().subtract(const Duration(days: 1)));

    if (lastDate == today) return;

    if (lastDate == yesterday) {
      _streak = streak + 1;
    } else {
      _streak = 1;
    }

    await prefs.setInt('streak', _streak);
    await prefs.setString('last_vote_date', today);
    notifyListeners();
  }
}
