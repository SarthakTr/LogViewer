import 'dart:io';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:path_provider/path_provider.dart';

void main() => runApp(const LogAnalysisApp());

class LogAnalysisApp extends StatelessWidget {
  const LogAnalysisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Log Analysis App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        textTheme: const TextTheme(
          bodyMedium: TextStyle(fontSize: 16.0, color: Colors.black87),
        ),
        scaffoldBackgroundColor: Colors.white,
      ),
      home: const LogScreen(),
    );
  }
}

class LogScreen extends StatefulWidget {
  const LogScreen({super.key});

  @override
  _LogScreenState createState() => _LogScreenState();
}

class _LogScreenState extends State<LogScreen> {
  List<Map<String, String>> _logEntries = [];
  final List<String> _selectedLogLevels = ['F', 'E', 'W'];
  Timer? _timer;
  String? _sessionId;
  bool _dataLoaded = false;

  Future<void> _fetchLogs(String action) async {
    String url;
    if (Platform.isAndroid) {
      url = action == 'start'
          ? 'http://192.168.149.51:8080/android/start'
          : 'http://192.168.149.51:8080/android/stop/$_sessionId';
    } else if (Platform.isIOS) {
      url = action == 'start'
          ? 'http://192.168.149.51:8080/ios/start'
          : 'http://192.168.149.51:8080/ios/stop/$_sessionId';
    } else {
      return;
    }

    try {
      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        if (action == 'start') {
          final responseData = json.decode(response.body);
          _sessionId = responseData["session_id"];
          if (kDebugMode) {
            print("Logcat started with session ID: $_sessionId");
          }

          _timer = Timer(const Duration(seconds: 2), () {
            _fetchLogs("stop");
          });
        } else if (action == 'stop') {
          // if (kDebugMode) {
          //   print("Received log data: ${response.body}");
          // }
          List<Map<String, String>> parsedCsv = _parseJsonLogs(response.body);

          // Debugging output
          if (kDebugMode) {
            print("Parsed log entries: $parsedCsv");
          }

          setState(() {
            _logEntries = parsedCsv.isNotEmpty
                ? parsedCsv
                : [
                    {'Error': 'No log entries found'}
                  ];
            _dataLoaded = true;
          });
        }
      } else {
        setState(() {
          _logEntries = [
            {'Error': 'Failed to fetch logs'}
          ];
        });
      }
    } catch (e) {
      setState(() {
        _logEntries = [
          {'Error': 'Network or parsing error'}
        ];
      });
      if (kDebugMode) {
        print("Error: $e");
      }
    }
  }

  List<Map<String, String>> _parseJsonLogs(String jsonContent) {
    try {
      // Decode the JSON content
      final List<dynamic> jsonData = json.decode(jsonContent);
      // Convert each JSON object into a Map<String, String>
      return jsonData.map((item) {
        return {
          'PID': (item['PID'] ?? '').toString(),
          'TID': (item['TID'] ?? '').toString(),
          'Log Level': (item['Log Level'] ?? '').toString(),
          'Component': (item['Component'] ?? '').toString(),
          'Content': (item['Content'] ?? '').toString(),
        };
      }).toList();
    } catch (e) {
      if (kDebugMode) {
        print("Error parsing JSON logs: $e");
      }
      return [];
    }
  }

  List<Map<String, String>> _filteredLogs() {
    if (_selectedLogLevels.length == 3) {
      return _logEntries;
    }
    return _logEntries
        .where((log) => _selectedLogLevels.contains(log['Log Level']))
        .toList();
  }

  Future<void> _downloadLogs() async {
    if (_sessionId == null) return;

    final downloadUrl = 'http://192.168.149.51:8080/download/$_sessionId';

    try {
      final response = await http.get(Uri.parse(downloadUrl));
      if (response.statusCode == 200) {
        final directory = await getDownloadsDirectory();
        final filePath = '${directory?.path}/logs_$_sessionId.csv';
        final file = File(filePath);
        await file.writeAsString(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Logs downloaded to $filePath')));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to download logs')));
      }
    } catch (e) {
      if (kDebugMode) {
        print("Error downloading logs: $e");
      }
    }
  }

  void _startLogging() {
    _fetchLogs('start');
  }

  void _stopLogging() {
    if (_sessionId != null) {
      _fetchLogs('stop');
      _timer?.cancel();
    } else {
      if (kDebugMode) {
        print("No session ID to stop logging.");
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Log Analysis App'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: _startLogging,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 30, vertical: 15),
                    textStyle: const TextStyle(fontSize: 18),
                  ),
                  child: const Text('Start'),
                ),
                const SizedBox(width: 20),
                ElevatedButton(
                  onPressed: _stopLogging,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 30, vertical: 15),
                    textStyle: const TextStyle(fontSize: 18),
                  ),
                  child: const Text('Stop'),
                ),
              ],
            ),
            const SizedBox(height: 20),
            if (_dataLoaded) _buildFilterDropdown(),
            const SizedBox(height: 20),
            if (_dataLoaded) _buildDownloadButton(),
            const SizedBox(height: 20),
            if (_dataLoaded)
              Expanded(
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: SingleChildScrollView(
                    scrollDirection: Axis.vertical,
                    child: _buildDataTable(),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterDropdown() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        DropdownButton<String>(
          value: null,
          hint: const Text('Filter'),
          items: ['F', 'E', 'W'].map((String level) {
            return DropdownMenuItem<String>(
              value: level,
              child: Row(
                children: [
                  Checkbox(
                    value: _selectedLogLevels.contains(level),
                    onChanged: (bool? value) {
                      setState(() {
                        if (value == true) {
                          _selectedLogLevels.add(level);
                        } else {
                          _selectedLogLevels.remove(level);
                        }
                      });
                    },
                  ),
                  Text(level),
                ],
              ),
            );
          }).toList(),
          onChanged: (_) {
            setState(() {}); // Update the parent state
          },
        ),
      ],
    );
  }

  Widget _buildDownloadButton() {
    return ElevatedButton(
      onPressed: _downloadLogs,
      child: const Text('Download Logs'),
    );
  }

  Widget _buildDataTable() {
    return DataTable(
      border: TableBorder.all(color: Colors.grey),
      columns: const [
        DataColumn(label: Text('PID')),
        DataColumn(label: Text('TID')),
        DataColumn(label: Text('Log Level')),
        DataColumn(label: Text('Component')),
        DataColumn(label: Text('Content')),
      ],
      rows: _filteredLogs().asMap().entries.map((entry) {
        int index = entry.key;
        Map<String, String> logEntry = entry.value;

        return DataRow(
          color: WidgetStateProperty.resolveWith<Color?>(
            (Set<WidgetState> states) {
              return index % 2 == 0 ? Colors.grey[100] : Colors.white;
            },
          ),
          cells: [
            DataCell(Text(logEntry['PID'] ?? '')),
            DataCell(Text(logEntry['TID'] ?? '')),
            DataCell(Text(logEntry['Log Level'] ?? '')),
            DataCell(Text(logEntry['Component'] ?? '')),
            DataCell(
              ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 300),
                child: Text(
                  logEntry['Content'] ?? '',
                  softWrap: true, // Enables wrapping
                  maxLines:
                      5, // Set to a reasonable number of lines for wrapping
                  overflow: TextOverflow
                      .ellipsis, // Shows ellipsis after maxLines are reached
                ),
              ),
            ),
          ],
        );
      }).toList(),
    );
  }
}
