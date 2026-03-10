import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';

class ChatService {
  static const String _prefKeyUrl = 'backend_url';
  static const String _prefKeySession = 'session_id';
  static const String _defaultUrl = 'http://10.0.2.2:8000'; // Android emulator → localhost

  final _uuid = const Uuid();

  // ── Persistent settings ─────────────────────────────────────────────────

  Future<String> getBackendUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_prefKeyUrl) ?? _defaultUrl;
  }

  Future<void> setBackendUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefKeyUrl, url.trim().trimRight().replaceAll(RegExp(r'/+$'), ''));
  }

  Future<String> getSessionId() async {
    final prefs = await SharedPreferences.getInstance();
    String? id = prefs.getString(_prefKeySession);
    if (id == null) {
      id = _uuid.v4();
      await prefs.setString(_prefKeySession, id);
    }
    return id;
  }

  Future<void> resetSession() async {
    final prefs = await SharedPreferences.getInstance();
    final newId = _uuid.v4();
    await prefs.setString(_prefKeySession, newId);
  }

  // ── Chat ────────────────────────────────────────────────────────────────

  /// Send a message and get a full (non-streaming) response.
  Future<String> sendMessage(String message) async {
    final baseUrl = await getBackendUrl();
    final sessionId = await getSessionId();

    final response = await http.post(
      Uri.parse('$baseUrl/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'session_id': sessionId,
        'message': message,
      }),
    ).timeout(const Duration(seconds: 60));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['reply'] as String;
    } else {
      throw Exception('Server error ${response.statusCode}: ${response.body}');
    }
  }

  // ── History ─────────────────────────────────────────────────────────────

  Future<List<Map<String, dynamic>>> getHistory() async {
    final baseUrl = await getBackendUrl();
    final sessionId = await getSessionId();

    final response = await http.get(
      Uri.parse('$baseUrl/history/$sessionId'),
    ).timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<Map<String, dynamic>>.from(data['messages']);
    } else {
      throw Exception('Failed to fetch history: ${response.statusCode}');
    }
  }

  // ── Clear ───────────────────────────────────────────────────────────────

  Future<void> clearHistory() async {
    final baseUrl = await getBackendUrl();
    final sessionId = await getSessionId();

    await http.delete(
      Uri.parse('$baseUrl/clear/$sessionId'),
    ).timeout(const Duration(seconds: 15));
  }

  // ── Health ──────────────────────────────────────────────────────────────

  Future<bool> checkHealth() async {
    try {
      final baseUrl = await getBackendUrl();
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
      ).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
