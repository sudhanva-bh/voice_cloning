import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'services/audio_converter.dart';
import 'services/recorder_service.dart';
import 'services/tts_service.dart';
import 'widgets/audio_player_widget.dart';

void main() => runApp(const VoiceCloneApp());

class VoiceCloneApp extends StatelessWidget {
  const VoiceCloneApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Voice Clone',
        theme: ThemeData.dark(useMaterial3: true).copyWith(
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.deepPurple,
            brightness: Brightness.dark,
          ),
        ),
        home: const HomeScreen(),
        debugShowCheckedModeBanner: false,
      );
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _recorder = RecorderService();
  final _tts = TtsService();

  final _refTextController = TextEditingController();
  final _targetTextController = TextEditingController();

  bool _isRecording = false;
  bool _isGenerating = false;
  bool _ttsReady = false;
  String? _refClipPath;
  String? _refFileName;
  List<File> _history = [];

  @override
  void initState() {
    super.initState();
    _loadCache();
    _tts.init().then((_) => setState(() => _ttsReady = true));
    _loadHistory();
    _refTextController.addListener(_saveCache);
    _targetTextController.addListener(_saveCache);
  }

  Future<void> _loadCache() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _refClipPath = prefs.getString('refClipPath');
      _refFileName = prefs.getString('refFileName');
      _refTextController.text = prefs.getString('refText') ?? '';
      _targetTextController.text = prefs.getString('targetText') ?? '';
    });
  }

  Future<void> _saveCache() async {
    final prefs = await SharedPreferences.getInstance();
    if (_refClipPath != null) {
      await prefs.setString('refClipPath', _refClipPath!);
      if (_refFileName != null) await prefs.setString('refFileName', _refFileName!);
    } else {
      await prefs.remove('refClipPath');
      await prefs.remove('refFileName');
    }
    await prefs.setString('refText', _refTextController.text);
    await prefs.setString('targetText', _targetTextController.text);
  }

  Future<void> _loadHistory() async {
    final dir = await getApplicationDocumentsDirectory();
    final files = dir.listSync().whereType<File>().where((f) => f.path.contains('generated_')).toList();
    files.sort((a, b) => b.lastModifiedSync().compareTo(a.lastModifiedSync()));
    if (mounted) setState(() => _history = files);
  }

  Future<void> _deleteClip(File file) async {
    if (await file.exists()) {
      await file.delete();
    }
    await _loadHistory();
  }

  Future<void> _downloadClip(File file) async {
    final format = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Export Format'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: ['WAV', 'MP3', 'OGG', 'M4A'].map((f) => 
             ListTile(
               title: Text(f),
               onTap: () => Navigator.pop(context, f),
             )
          ).toList(),
        ),
      ),
    );
    if (format == null) return;

    try {
      // Request permission for older Androids. We intentionally ignore the result here
      // because on Android 13+ this request will be denied, but we are still natively
      // allowed to write to the public Downloads folder!
      await Permission.storage.request();
      
      setState(() => _isGenerating = true);
      final outFormatPath = await AudioConverter.convertFormat(file.path, format);
      setState(() => _isGenerating = false);
      
      if (outFormatPath == null) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to convert format'), backgroundColor: Colors.red));
        return;
      }
      
      final downloadsDir = Directory('/storage/emulated/0/Download');
      if (!await downloadsDir.exists()) {
         await downloadsDir.create(recursive: true);
      }
      
      final outFormatFile = File(outFormatPath);
      final originalBase = file.path.split(Platform.pathSeparator).last.replaceAll(RegExp(r'\.[^.]+$'), '');
      final finalName = '$originalBase.${format.toLowerCase()}';
      
      final savePath = '${downloadsDir.path}/$finalName';
      await outFormatFile.copy(savePath);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Saved to Downloads: $finalName'), backgroundColor: Colors.green),
        );
      }
    } catch (e) {
      if (mounted) {
         setState(() => _isGenerating = false);
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Failed to save: $e'), backgroundColor: Colors.red),
         );
      }
    }
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      final path = await _recorder.stop();
      setState(() {
        _isRecording = false;
        _isGenerating = true; // reuse loading state for conversion
      });
      if (path != null) {
        final wavPath = await AudioConverter.convertToWav(path);
        setState(() {
          _isGenerating = false;
          if (wavPath != null) {
            _refClipPath = wavPath;
            _refFileName = 'recording';
            _saveCache();
          }
        });
      } else {
        setState(() => _isGenerating = false);
      }
    } else {
      await _recorder.start();
      setState(() => _isRecording = true);
    }
  }

  Future<void> _pickAudio() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.audio);
    if (result != null && result.files.single.path != null) {
      final inputPath = result.files.single.path!;
      setState(() => _isGenerating = true);
      
      final wavPath = await AudioConverter.convertToWav(inputPath);
      
      setState(() {
        _isGenerating = false;
        if (wavPath != null) {
          _refClipPath = wavPath;
          _refFileName = result.files.single.name.replaceAll(RegExp(r'\.[^.]+$'), '');
          _saveCache();
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to convert audio file')),
          );
        }
      });
    }
  }

  Future<void> _generate() async {
    if (_refClipPath == null || _refTextController.text.isEmpty) return;
    setState(() => _isGenerating = true);

    try {
      // Validate WAV header
      final file = File(_refClipPath!);
      if (!await file.exists()) throw Exception('File not found');
      
      final raf = await file.open(mode: FileMode.read);
      final header = await raf.read(4);
      await raf.close();
      
      final isRiff = header.length == 4 && String.fromCharCodes(header) == 'RIFF';
      if (!isRiff) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Error: Reference clip must be a valid WAV file. Please record a new clip or upload a valid WAV file.'),
              backgroundColor: Colors.red,
            ),
          );
        }
        return;
      }

      final dir = await getApplicationDocumentsDirectory();
      final baseName = _refFileName ?? 'recording';
      final outPath =
          '${dir.path}/${baseName}_generated_${DateTime.now().millisecondsSinceEpoch}.wav';

      final result = await _tts.generate(
        referenceWavPath: _refClipPath!,
        referenceText: _refTextController.text,
        targetText: _targetTextController.text,
        outputWavPath: outPath,
      );
      
      final rtfStr = result.rtf.toStringAsFixed(3);
      final rssStr = result.rssMB.toString();
      final newOutPath = outPath.replaceFirst('_generated_', '_generated_rtf_${rtfStr}_rss_${rssStr}_');
      await File(outPath).rename(newOutPath);

      await _loadHistory();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Voice cloning complete!'),
            behavior: SnackBarBehavior.floating,
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isGenerating = false);
    }
  }

  String? _extractRtf(String filename) {
    final match = RegExp(r'_generated_rtf_([0-9.]+)_').firstMatch(filename);
    return match?.group(1);
  }

  String? _extractRss(String filename) {
    final match = RegExp(r'_rss_([0-9]+)_').firstMatch(filename);
    return match?.group(1);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice Clone Prototype'),
        centerTitle: true,
        elevation: 2,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (!_ttsReady) ...[
                const LinearProgressIndicator(),
                const SizedBox(height: 16),
                const Center(child: Text('Initializing offline TTS engine...')),
                const SizedBox(height: 24),
              ],
              _buildStepCard(
                context,
                title: 'Step 1: Reference clip',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (_refClipPath != null)
                      Row(
                        children: [
                          Expanded(
                            child: AudioPlayerWidget(
                              key: ValueKey(_refClipPath),
                              filePath: _refClipPath!,
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.upload_file),
                            tooltip: 'Upload new clip',
                            onPressed: _pickAudio,
                          ),
                          IconButton(
                            icon: const Icon(Icons.refresh),
                            tooltip: 'Reset clip',
                            onPressed: () => setState(() {
                              _refClipPath = null;
                              _refFileName = null;
                              _saveCache();
                            }),
                          ),
                        ],
                      )
                    else
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.all(16),
                                backgroundColor: _isRecording ? Colors.redAccent : null,
                                foregroundColor: _isRecording ? Colors.white : null,
                              ),
                              onPressed: _toggleRecording,
                              icon: Icon(_isRecording ? Icons.stop : Icons.mic),
                              label: Text(
                                _isRecording ? 'Stop' : 'Record',
                                style: const TextStyle(fontSize: 16),
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.all(16),
                              ),
                              onPressed: _isRecording ? null : _pickAudio,
                              icon: const Icon(Icons.upload_file),
                              label: const Text('Upload', style: TextStyle(fontSize: 16)),
                            ),
                          ),
                        ],
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              _buildStepCard(
                context,
                title: 'Step 2: Transcript of that clip',
                child: TextField(
                  controller: _refTextController,
                  maxLines: null,
                  minLines: 3,
                  textCapitalization: TextCapitalization.sentences,
                  decoration: const InputDecoration(
                    hintText: 'Type here',
                    border: OutlineInputBorder(),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              _buildStepCard(
                context,
                title: 'Type here',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    TextField(
                      controller: _targetTextController,
                      maxLines: null,
                      minLines: 3,
                      textCapitalization: TextCapitalization.sentences,
                      decoration: const InputDecoration(
                        hintText: 'Text you want spoken in the cloned voice',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    FilledButton(
                      style: FilledButton.styleFrom(
                        padding: const EdgeInsets.all(16),
                      ),
                      onPressed: (_ttsReady && !_isGenerating && _refClipPath != null)
                          ? _generate
                          : null,
                      child: _isGenerating
                          ? const SizedBox(
                              height: 24,
                              width: 24,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Generate cloned speech', style: TextStyle(fontSize: 16)),
                    ),
                  ],
                ),
              ),
              if (_history.isNotEmpty) ...[
                const SizedBox(height: 24),
                Center(
                  child: Text(
                    'Generated Clips',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(height: 16),
                _buildStepCard(
                  context,
                  title: 'Latest Generation',
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _history.first.path.split(Platform.pathSeparator).last,
                                  style: Theme.of(context).textTheme.bodyMedium,
                                ),
                                if (_extractRtf(_history.first.path) != null)
                                  Padding(
                                    padding: const EdgeInsets.only(top: 4),
                                    child: Row(
                                      children: [
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: Colors.green.withOpacity(0.2),
                                            borderRadius: BorderRadius.circular(12),
                                          ),
                                          child: Text('RTF: ${_extractRtf(_history.first.path)}x', style: const TextStyle(fontSize: 12, color: Colors.greenAccent)),
                                        ),
                                        if (_extractRss(_history.first.path) != null) ...[
                                          const SizedBox(width: 8),
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                            decoration: BoxDecoration(
                                              color: Colors.blue.withOpacity(0.2),
                                              borderRadius: BorderRadius.circular(12),
                                            ),
                                            child: Text('RSS: ${_extractRss(_history.first.path)} MB', style: const TextStyle(fontSize: 12, color: Colors.blueAccent)),
                                          ),
                                        ],
                                      ],
                                    ),
                                  ),
                              ],
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.download_rounded, color: Colors.blueAccent),
                            tooltip: 'Download',
                            onPressed: () => _downloadClip(_history.first),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      AudioPlayerWidget(filePath: _history.first.path, key: ValueKey(_history.first.path)),
                    ],
                  ),
                ),
                if (_history.length > 1) ...[
                  const SizedBox(height: 16),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 8),
                    child: Text('Older Clips:', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  const SizedBox(height: 8),
                  ..._history.skip(1).map((file) {
                    final filename = file.path.split(Platform.pathSeparator).last;
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Expanded(child: Text(filename, style: const TextStyle(fontSize: 14))),
                                      if (_extractRtf(filename) != null)
                                        Container(
                                          margin: const EdgeInsets.only(left: 8),
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: Colors.green.withOpacity(0.2),
                                            borderRadius: BorderRadius.circular(12),
                                          ),
                                          child: Text('RTF: ${_extractRtf(filename)}x', style: const TextStyle(fontSize: 12, color: Colors.greenAccent)),
                                        ),
                                      if (_extractRss(filename) != null)
                                        Container(
                                          margin: const EdgeInsets.only(left: 8),
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: Colors.blue.withOpacity(0.2),
                                            borderRadius: BorderRadius.circular(12),
                                          ),
                                          child: Text('RSS: ${_extractRss(filename)} MB', style: const TextStyle(fontSize: 12, color: Colors.blueAccent)),
                                        ),
                                    ],
                                  ),
                                  AudioPlayerWidget(filePath: file.path, key: ValueKey(file.path)),
                                ],
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.download_rounded, color: Colors.blueAccent),
                              tooltip: 'Download',
                              onPressed: () => _downloadClip(file),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete, color: Colors.redAccent),
                              onPressed: () => _deleteClip(file),
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                ],
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStepCard(BuildContext context, {required String title, required Widget child}) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              title,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            child,
          ],
        ),
      ),
    );
  }
}
