import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:contoh/models/message.dart';

void main() {
  test('Message model test', () {
    final msg = Message(
      id: '1',
      content: 'Hello',
      isUser: true,
      timestamp: DateTime.now(),
    );
    expect(msg.content, 'Hello');
    expect(msg.isUser, true);
  });
}
