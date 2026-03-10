import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ── Color Palette ────────────────────────────────────────────────────────
  static const Color bgDark = Color(0xFF0A0E1A);       // deep navy black
  static const Color bgSurface = Color(0xFF111827);    // card background
  static const Color bgCard = Color(0xFF1A2236);       // elevated card
  static const Color accent = Color(0xFF3B82F6);       // electric blue
  static const Color accentLight = Color(0xFF60A5FA);  // light blue
  static const Color accentGlow = Color(0x333B82F6);   // translucent blue
  static const Color userBubble = Color(0xFF1D4ED8);   // user message
  static const Color aiBubble = Color(0xFF1E293B);     // AI message
  static const Color textPrimary = Color(0xFFF1F5F9);  // primary text
  static const Color textSecondary = Color(0xFF94A3B8); // secondary text
  static const Color textMuted = Color(0xFF475569);    // muted text
  static const Color divider = Color(0xFF1E293B);
  static const Color error = Color(0xFFEF4444);
  static const Color success = Color(0xFF10B981);

  // ── Gradients ───────────────────────────────────────────────────────────
  static const LinearGradient backgroundGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Color(0xFF0A0E1A), Color(0xFF0D1424)],
  );

  static const LinearGradient accentGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF3B82F6), Color(0xFF8B5CF6)],
  );

  static const LinearGradient userBubbleGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF1D4ED8), Color(0xFF2563EB)],
  );

  // ── Theme Data ──────────────────────────────────────────────────────────
  static ThemeData get dark {
    final textTheme = GoogleFonts.interTextTheme(ThemeData.dark().textTheme);
    return ThemeData.dark().copyWith(
      scaffoldBackgroundColor: bgDark,
      colorScheme: const ColorScheme.dark(
        primary: accent,
        secondary: accentLight,
        surface: bgSurface,
        error: error,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: textPrimary,
      ),
      textTheme: textTheme.copyWith(
        displayLarge: textTheme.displayLarge?.copyWith(color: textPrimary),
        bodyLarge: textTheme.bodyLarge?.copyWith(color: textPrimary),
        bodyMedium: textTheme.bodyMedium?.copyWith(color: textPrimary),
        bodySmall: textTheme.bodySmall?.copyWith(color: textSecondary),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: bgDark,
        elevation: 0,
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
        iconTheme: IconThemeData(color: textPrimary),
      ),
      dividerColor: divider,
      cardColor: bgCard,
    );
  }
}
