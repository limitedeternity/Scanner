import 'package:flutter/material.dart';
import 'package:scanner/app.dart';

void main() {
  runApp(Scanner());
}

class Scanner extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Scanner",
      theme: ThemeData(
        primarySwatch: Colors.teal,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      debugShowCheckedModeBanner: false,
      home: Application(),
    );
  }
}
