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
          cardTheme: CardThemeData(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          ),
        ),
        home: const HomeScreen(),
        debugShowCheckedModeBanner: false,
      );
}

class ExampleTranscript {
  final String title;
  final String advantage;
  final String text;

  const ExampleTranscript({
    required this.title,
    required this.advantage,
    required this.text,
  });
}

enum IdeaSection { short, medium, long }

class QuickIdea {
  final String text;
  final IdeaSection section;

  const QuickIdea({
    required this.text,
    required this.section,
  });
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

  static const List<ExampleTranscript> _exampleTranscripts = [
    ExampleTranscript(
      title: 'Casual & Conversational',
      advantage: 'Natural flow & cadence',
      text:
          "Honestly, I'm just hanging out at home today and trying to catch up on some things. The weather is actually pretty nice outside, so I might go for a quick walk later. Let me know what your schedule looks like, and maybe we can grab some food.",
    ),
    ExampleTranscript(
      title: 'Phonetic Variety',
      advantage: 'Full pangram coverage',
      text:
          'The quick brown fox jumps over the lazy dog, while the five boxing wizards jump quickly and quiet owls hoot after midnight.',
    ),
    ExampleTranscript(
      title: 'Phonetic Coverage',
      advantage: 'Nuanced sounds & vowels',
      text:
          'The beige hue on the waters of the loch impressed all, including the French queen, before she heard that symphony again.',
    ),
    ExampleTranscript(
      title: 'Professional Narration',
      advantage: 'Clear formal pacing',
      text:
          'Welcome to the voice cloning demonstration. Accurate pronunciation and consistent pacing ensure the highest quality voice synthesis.',
    ),
  ];

  static const List<QuickIdea> _quickIdeas = [
    // --- SHORT TEXTS ---
    QuickIdea(
      section: IdeaSection.short,
      text: 'Hello! This is a quick test of the voice cloning system.',
    ),
    QuickIdea(
      section: IdeaSection.short,
      text: 'How are you doing today? Hope everything is going well.',
    ),
    QuickIdea(
      section: IdeaSection.short,
      text: 'Your voice model has been synthesized successfully.',
    ),

    // --- MEDIUM TEXTS ---
    QuickIdea(
      section: IdeaSection.medium,
      text:
          'Artificial intelligence is rapidly transforming how we communicate across different languages and cultures. With on-device neural voice cloning, you can generate natural speech in real time without relying on cloud servers or internet access.',
    ),
    QuickIdea(
      section: IdeaSection.medium,
      text:
          'The weather is exceptionally pleasant outside this afternoon, with a gentle cool breeze and clear blue skies. It would be a great time to step out for a quick walk, catch some fresh air, and grab a cup of coffee.',
    ),
    QuickIdea(
      section: IdeaSection.medium,
      text:
          'Voice cloning technology captures the subtle acoustic nuances, vocal timbre, and cadence of a human speaker. When combined with fast local inference engines, it opens up brand new possibilities for audiobooks, podcasts, and personal voice assistants.',
    ),

    // --- LONG TEXTS ---
    QuickIdea(
      section: IdeaSection.long,
      text:
          'The morning sun rose gently above the rolling green hills, casting a warm golden glow across the quiet valley below. A flock of wild geese soared gracefully against the amber dawn, while a cool morning mist slowly drifted through the pine forest. In the distance, the gentle rush of a mountain stream blended harmoniously with the awakening sounds of nature, creating a serene and timeless atmosphere that felt entirely separate from the busy modern world.',
    ),
    QuickIdea(
      section: IdeaSection.long,
      text:
          'Neural speech synthesis represents a monumental breakthrough in modern computational linguistics and audio engineering. By modeling complex acoustic representations, high-order harmonics, and natural conversational prosody, state-of-the-art generative models produce synthetic speech virtually indistinguishable from live human recordings. This enables seamless multilingual dubbing, accessible voice restoration for individuals with speech impairments, and personalized interactive agents running completely on device.',
    ),
    QuickIdea(
      section: IdeaSection.long,
      text:
          'Beyond the ancient stone gateway lay a winding cobblestone path that had remained untouched for centuries. Towering cedar trees lined the pathway on either side, their thick branches forming a natural canopy that whispered softly whenever the wind swept through the canyon. Every step forward revealed another chapter of history, reminding every traveler of the countless generations who had walked these grounds before.',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _loadCache();
    _tts.init().then((_) => setState(() => _ttsReady = true));
    _loadHistory();
    _refTextController.addListener(_saveCache);
    _targetTextController.addListener(_saveCache);
  }

  @override
  void dispose() {
    _refTextController.dispose();
    _targetTextController.dispose();
    super.dispose();
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
        title: const Text('Select Export Format', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: ['WAV', 'MP3', 'OGG', 'M4A']
              .map((f) => ListTile(
                    title: Text(f, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14.5)),
                    trailing: const Icon(Icons.download_rounded, size: 20),
                    onTap: () => Navigator.pop(context, f),
                  ))
              .toList(),
        ),
      ),
    );
    if (format == null) return;

    try {
      await Permission.storage.request();

      setState(() => _isGenerating = true);
      final outFormatPath = await AudioConverter.convertFormat(file.path, format);
      setState(() => _isGenerating = false);

      if (outFormatPath == null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to convert format'), backgroundColor: Colors.red),
          );
        }
        return;
      }

      final downloadsDir = Directory('/storage/emulated/0/Download');
      if (!await downloadsDir.exists()) {
        await downloadsDir.create(recursive: true);
      }

      final outFormatFile = File(outFormatPath);
      final originalBase =
          _formatDisplayTitle(file.path.split(Platform.pathSeparator).last);
      final finalName = '$originalBase.${format.toLowerCase()}';

      final savePath = '${downloadsDir.path}/$finalName';
      await outFormatFile.copy(savePath);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Saved to Downloads: $finalName'),
            backgroundColor: Colors.green,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isGenerating = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save: $e'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      final path = await _recorder.stop();
      setState(() {
        _isRecording = false;
        _isGenerating = true;
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
    if (_refClipPath == null || _refTextController.text.trim().isEmpty) return;
    if (_targetTextController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter target text to synthesize.'),
          backgroundColor: Colors.orange,
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    setState(() => _isGenerating = true);

    try {
      final file = File(_refClipPath!);
      if (!await file.exists()) throw Exception('Reference audio file not found');

      final raf = await file.open(mode: FileMode.read);
      final header = await raf.read(4);
      await raf.close();

      final isRiff = header.length == 4 && String.fromCharCodes(header) == 'RIFF';
      if (!isRiff) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                  'Error: Reference clip must be a valid WAV file. Please record a new clip or upload a valid audio file.'),
              backgroundColor: Colors.red,
            ),
          );
        }
        return;
      }

      final dir = await getApplicationDocumentsDirectory();
      final now = DateTime.now();
      final day = now.day.toString().padLeft(2, '0');
      final month = now.month.toString().padLeft(2, '0');
      final year = now.year.toString();
      final hour = now.hour.toString().padLeft(2, '0');
      final minute = now.minute.toString().padLeft(2, '0');
      final timeStamp = '${day}_${month}_${year}__${hour}_${minute}';
      final baseTitle = 'generated_$timeStamp';

      final outPath =
          '${dir.path}/${baseTitle}_${now.millisecondsSinceEpoch}.wav';

      final result = await _tts.generate(
        referenceWavPath: _refClipPath!,
        referenceText: _refTextController.text.trim(),
        targetText: _targetTextController.text.trim(),
        outputWavPath: outPath,
      );

      final rtfStr = result.rtf.toStringAsFixed(3);
      final rssStr = result.rssMB.toString();
      final newOutPath =
          '${dir.path}/${baseTitle}_rtf_${rtfStr}_rss_${rssStr}_${now.millisecondsSinceEpoch}.wav';
      await File(outPath).rename(newOutPath);

      await _loadHistory();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Voice cloning complete! Scroll down to listen.'),
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
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      setState(() => _isGenerating = false);
    }
  }

  String? _extractRtf(String filename) {
    final match = RegExp(r'_rtf_([0-9.]+)_').firstMatch(filename);
    return match?.group(1);
  }

  String? _extractRss(String filename) {
    final match = RegExp(r'_rss_([0-9]+)_').firstMatch(filename);
    return match?.group(1);
  }

  String _formatDisplayTitle(String filename) {
    final match = RegExp(r'(generated_\d{2}_\d{2}_\d{4}__\d{2}_\d{2})').firstMatch(filename);
    if (match != null) {
      return match.group(1)!;
    }
    return filename
        .replaceAll(RegExp(r'_rtf_[0-9.]+_rss_[0-9]+_'), '_')
        .replaceAll(RegExp(r'_\d+\.wav$'), '')
        .replaceAll(RegExp(r'\.wav$'), '');
  }

  Widget _buildScriptCard(ExampleTranscript item) {
    final isSelected = _refTextController.text.trim() == item.text.trim();
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: isSelected
            ? Colors.deepPurple.withValues(alpha: 0.25)
            : Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.35),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: isSelected ? Colors.deepPurpleAccent : Colors.white12,
          width: isSelected ? 1.5 : 1,
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(10),
          onTap: () {
            setState(() => _refTextController.text = item.text);
            Navigator.pop(context);
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Reference script updated!'),
                duration: Duration(seconds: 2),
                behavior: SnackBarBehavior.floating,
              ),
            );
          },
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Text(
              item.text,
              style: TextStyle(
                fontSize: 13.5,
                color: Colors.white.withValues(alpha: 0.9),
                height: 1.35,
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _showExampleTranscriptsModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.of(context).size.height * 0.75,
            ),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.auto_stories_rounded, color: Colors.deepPurpleAccent, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Example Reference Scripts',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, size: 20),
                        visualDensity: VisualDensity.compact,
                        onPressed: () => Navigator.pop(context),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Tap any preset script to load into Step 1:',
                    style: TextStyle(fontSize: 13.5, color: Colors.white.withValues(alpha: 0.7)),
                  ),
                  const SizedBox(height: 8),
                  Expanded(
                    child: ListView(
                      children: _exampleTranscripts.expand((item) => [
                        _buildSectionHeader(
                          title: item.title,
                          badge: item.advantage,
                        ),
                        _buildScriptCard(item),
                      ]).toList(),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildIdeaCard(QuickIdea idea) {
    final isSelected = _targetTextController.text.trim() == idea.text.trim();
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: isSelected
            ? Colors.deepPurple.withValues(alpha: 0.25)
            : Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.35),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: isSelected ? Colors.deepPurpleAccent : Colors.white12,
          width: isSelected ? 1.5 : 1,
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(10),
          onTap: () {
            setState(() => _targetTextController.text = idea.text);
            Navigator.pop(context);
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Target text updated!'),
                duration: Duration(seconds: 2),
                behavior: SnackBarBehavior.floating,
              ),
            );
          },
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Text(
              idea.text,
              style: TextStyle(
                fontSize: 13.5,
                color: Colors.white.withValues(alpha: 0.9),
                height: 1.35,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader({
    required String title,
    required String badge,
  }) {
    return Padding(
      padding: const EdgeInsets.only(top: 12, bottom: 6),
      child: Row(
        children: [
          Text(
            title,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 14,
              color: Colors.deepPurpleAccent,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: Colors.deepPurpleAccent.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              badge,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: Colors.deepPurpleAccent.shade100,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showQuickIdeasModal() {
    final shortIdeas = _quickIdeas.where((i) => i.section == IdeaSection.short).toList();
    final mediumIdeas = _quickIdeas.where((i) => i.section == IdeaSection.medium).toList();
    final longIdeas = _quickIdeas.where((i) => i.section == IdeaSection.long).toList();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.of(context).size.height * 0.75,
            ),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.tips_and_updates_rounded, color: Colors.deepPurpleAccent, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Target Speech Ideas',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, size: 20),
                        visualDensity: VisualDensity.compact,
                        onPressed: () => Navigator.pop(context),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Tap any preset text to load into Step 3:',
                    style: TextStyle(fontSize: 13.5, color: Colors.white.withValues(alpha: 0.7)),
                  ),
                  const SizedBox(height: 8),
                  Expanded(
                    child: ListView(
                      children: [
                        // SECTION 1: SHORT
                        _buildSectionHeader(
                          title: 'Short',
                          badge: '1 sentence',
                        ),
                        ...shortIdeas.map(_buildIdeaCard),

                        // SECTION 2: MEDIUM
                        _buildSectionHeader(
                          title: 'Medium',
                          badge: '2–3 sentences',
                        ),
                        ...mediumIdeas.map(_buildIdeaCard),

                        // SECTION 3: LONG
                        _buildSectionHeader(
                          title: 'Long',
                          badge: 'Paragraph',
                        ),
                        ...longIdeas.map(_buildIdeaCard),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice Clone Studio', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        centerTitle: true,
        elevation: 2,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (!_ttsReady) ...[
                Card(
                  color: Colors.deepPurple.shade900.withValues(alpha: 0.4),
                  child: const Padding(
                    padding: EdgeInsets.all(14),
                    child: Column(
                      children: [
                        LinearProgressIndicator(),
                        SizedBox(height: 10),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.hourglass_top_rounded, size: 16),
                            SizedBox(width: 8),
                            Text(
                              'Initializing offline TTS engine...',
                              style: TextStyle(fontWeight: FontWeight.w500, fontSize: 13.5),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
              ],

              // STEP 1: Reference Script / Transcript (First)
              _buildStep1ReferenceTranscriptCard(),
              const SizedBox(height: 14),

              // STEP 2: Reference Voice Audio (Second)
              _buildStep2ReferenceAudioCard(),
              const SizedBox(height: 14),

              // STEP 3: Target Speech Text (Third)
              _buildStep3TargetTextCard(),
              const SizedBox(height: 16),

              // STEP 4: Cloned Output & Library (Fourth)
              _buildStep4OutputCard(),
            ],
          ),
        ),
      ),
    );
  }

  // --- STEP 1 WIDGET ---
  Widget _buildStep1ReferenceTranscriptCard() {
    final hasText = _refTextController.text.trim().isNotEmpty;
    return _buildSectionCard(
      stepNumber: '1',
      title: 'Reference Script (Transcript)',
      subtitle: 'Type what you will say in Step 2, or choose an example script.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              OutlinedButton.icon(
                onPressed: _showExampleTranscriptsModal,
                icon: const Icon(Icons.auto_stories_rounded, size: 17),
                label: const Text('Example Scripts', style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w500)),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  visualDensity: VisualDensity.compact,
                  foregroundColor: Colors.deepPurpleAccent.shade100,
                ),
              ),
              if (hasText)
                TextButton.icon(
                  onPressed: () => setState(() => _refTextController.clear()),
                  icon: const Icon(Icons.clear, size: 15),
                  label: const Text('Clear', style: TextStyle(fontSize: 13)),
                  style: TextButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    foregroundColor: Colors.white60,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _refTextController,
            maxLines: null,
            minLines: 2,
            style: const TextStyle(fontSize: 14.5),
            textCapitalization: TextCapitalization.sentences,
            decoration: InputDecoration(
              hintText: 'Type or choose reference transcript text...',
              hintStyle: TextStyle(fontSize: 14, color: Colors.white.withValues(alpha: 0.5)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.2),
            ),
          ),
        ],
      ),
    );
  }

  // --- STEP 2 WIDGET ---
  Widget _buildStep2ReferenceAudioCard() {
    final hasAudio = _refClipPath != null;
    return _buildSectionCard(
      stepNumber: '2',
      title: 'Reference Voice Audio',
      subtitle: 'Record yourself speaking the transcript, or upload an audio file.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (hasAudio) ...[
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.green.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.green.withValues(alpha: 0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.check_circle_rounded, color: Colors.greenAccent, size: 18),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          'Clip Ready (${_refFileName ?? "recording"})',
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            color: Colors.greenAccent,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.upload_file_rounded, size: 20),
                        tooltip: 'Upload new file',
                        visualDensity: VisualDensity.compact,
                        onPressed: _pickAudio,
                      ),
                      IconButton(
                        icon: const Icon(Icons.refresh_rounded, size: 20),
                        tooltip: 'Reset clip',
                        visualDensity: VisualDensity.compact,
                        onPressed: () => setState(() {
                          _refClipPath = null;
                          _refFileName = null;
                          _saveCache();
                        }),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  AudioPlayerWidget(
                    key: ValueKey(_refClipPath),
                    filePath: _refClipPath!,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: _toggleRecording,
              icon: Icon(_isRecording ? Icons.stop_rounded : Icons.mic_rounded, size: 18),
              label: Text(_isRecording ? 'Stop Re-recording' : 'Re-record Voice Clip',
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 10),
                visualDensity: VisualDensity.compact,
                foregroundColor: _isRecording ? Colors.redAccent : null,
              ),
            ),
          ] else ...[
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      backgroundColor: _isRecording ? Colors.redAccent : Colors.deepPurple,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: _toggleRecording,
                    icon: Icon(_isRecording ? Icons.stop_circle_rounded : Icons.mic_rounded, size: 20),
                    label: Text(
                      _isRecording ? 'Stop' : 'Record Audio',
                      style: const TextStyle(fontSize: 14.5, fontWeight: FontWeight.w600),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: _isRecording ? null : _pickAudio,
                    icon: const Icon(Icons.upload_file_rounded, size: 20),
                    label: const Text('Upload File',
                        style: TextStyle(fontSize: 14.5, fontWeight: FontWeight.w600)),
                  ),
                ),
              ],
            ),
            if (_isRecording)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: Colors.redAccent,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 6),
                    const Text(
                      'Recording... Read Step 1 transcript aloud',
                      style: TextStyle(color: Colors.redAccent, fontSize: 13, fontWeight: FontWeight.w500),
                    ),
                  ],
                ),
              ),
          ],
        ],
      ),
    );
  }

  // --- STEP 3 WIDGET ---
  Widget _buildStep3TargetTextCard() {
    final canGenerate = _ttsReady &&
        !_isGenerating &&
        _refClipPath != null &&
        _refTextController.text.trim().isNotEmpty &&
        _targetTextController.text.trim().isNotEmpty;

    final hasText = _targetTextController.text.trim().isNotEmpty;

    return _buildSectionCard(
      stepNumber: '3',
      title: 'Target Speech Text',
      subtitle: 'Enter what you want synthesized in the cloned voice.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              OutlinedButton.icon(
                onPressed: _showQuickIdeasModal,
                icon: const Icon(Icons.tips_and_updates_rounded, size: 17),
                label: const Text('Quick Ideas', style: TextStyle(fontSize: 13.5, fontWeight: FontWeight.w500)),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  visualDensity: VisualDensity.compact,
                  foregroundColor: Colors.deepPurpleAccent.shade100,
                ),
              ),
              if (hasText)
                TextButton.icon(
                  onPressed: () => setState(() => _targetTextController.clear()),
                  icon: const Icon(Icons.clear, size: 15),
                  label: const Text('Clear', style: TextStyle(fontSize: 13)),
                  style: TextButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    foregroundColor: Colors.white60,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _targetTextController,
            maxLines: null,
            minLines: 2,
            style: const TextStyle(fontSize: 14.5),
            textCapitalization: TextCapitalization.sentences,
            decoration: InputDecoration(
              hintText: 'Type sentence or paragraph to synthesize in cloned voice...',
              hintStyle: TextStyle(fontSize: 14, color: Colors.white.withValues(alpha: 0.5)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
              filled: true,
              fillColor: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.2),
            ),
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: canGenerate ? _generate : null,
            icon: _isGenerating
                ? const SizedBox(
                    height: 18,
                    width: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.record_voice_over_rounded, size: 20),
            label: Text(
              _isGenerating ? 'Synthesizing Cloned Voice...' : 'Generate Cloned Speech',
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
            ),
          ),
          if (!canGenerate && !_isGenerating) ...[
            const SizedBox(height: 6),
            Center(
              child: Text(
                _refClipPath == null
                    ? '⚠️ Step 2 audio required before generating.'
                    : _refTextController.text.trim().isEmpty
                        ? '⚠️ Step 1 transcript cannot be empty.'
                        : _targetTextController.text.trim().isEmpty
                            ? '💡 Enter target text above to generate.'
                            : 'Initializing engine...',
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.white.withValues(alpha: 0.65),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  // --- STEP 4 WIDGET ---
  Widget _buildStep4OutputCard() {
    if (_history.isEmpty) {
      return _buildSectionCard(
        stepNumber: '4',
        title: 'Generated Speech & Library',
        subtitle: 'Generated clips and export options will appear here.',
        child: Container(
          padding: const EdgeInsets.all(16),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: Colors.white12),
          ),
          child: Column(
            children: [
              Icon(Icons.audio_file_outlined, size: 32, color: Colors.white.withValues(alpha: 0.4)),
              const SizedBox(height: 6),
              Text(
                'No clips generated yet',
                style: TextStyle(color: Colors.white.withValues(alpha: 0.65), fontSize: 13.5, fontWeight: FontWeight.w500),
              ),
            ],
          ),
        ),
      );
    }

    final latestFile = _history.first;
    final latestFilename = latestFile.path.split(Platform.pathSeparator).last;
    final latestRtf = _extractRtf(latestFilename);
    final latestRss = _extractRss(latestFilename);

    return _buildSectionCard(
      stepNumber: '4',
      title: 'Generated Speech & Library',
      subtitle: 'Listen to and export your synthesized audio clips.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.deepPurple.shade900.withValues(alpha: 0.4),
                  Colors.deepPurple.shade800.withValues(alpha: 0.2),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.deepPurpleAccent.withValues(alpha: 0.5)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.deepPurpleAccent,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Text(
                        'LATEST',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                    const Spacer(),
                    IconButton.filledTonal(
                      icon: const Icon(Icons.download_rounded, size: 18),
                      tooltip: 'Export audio clip',
                      visualDensity: VisualDensity.compact,
                      onPressed: () => _downloadClip(latestFile),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  _formatDisplayTitle(latestFilename),
                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                ),
                if (latestRtf != null || latestRss != null) ...[
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 6,
                    runSpacing: 4,
                    children: [
                      if (latestRtf != null)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.green.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.4)),
                          ),
                          child: Text(
                            'RTF: ${latestRtf}x',
                            style: const TextStyle(
                              fontSize: 12,
                              color: Colors.greenAccent,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      if (latestRss != null)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.blue.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.4)),
                          ),
                          child: Text(
                            'Memory: $latestRss MB',
                            style: const TextStyle(
                              fontSize: 12,
                              color: Colors.blueAccent,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
                const SizedBox(height: 8),
                AudioPlayerWidget(filePath: latestFile.path, key: ValueKey(latestFile.path)),
              ],
            ),
          ),
          if (_history.length > 1) ...[
            const SizedBox(height: 12),
            Text(
              'Previous Generations (${_history.length - 1}):',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold, fontSize: 14),
            ),
            const SizedBox(height: 6),
            ..._history.skip(1).map((file) {
              final filename = file.path.split(Platform.pathSeparator).last;
              final rtf = _extractRtf(filename);
              final rss = _extractRss(filename);

              return Card(
                margin: const EdgeInsets.only(bottom: 6),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                child: Padding(
                  padding: const EdgeInsets.all(10),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              _formatDisplayTitle(filename),
                              style: const TextStyle(fontSize: 13.5, fontWeight: FontWeight.w500),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.download_rounded, color: Colors.blueAccent, size: 18),
                            tooltip: 'Export',
                            onPressed: () => _downloadClip(file),
                            visualDensity: VisualDensity.compact,
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete_outline_rounded, color: Colors.redAccent, size: 18),
                            tooltip: 'Delete',
                            onPressed: () => _deleteClip(file),
                            visualDensity: VisualDensity.compact,
                          ),
                        ],
                      ),
                      if (rtf != null || rss != null)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            children: [
                              if (rtf != null)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                                  margin: const EdgeInsets.only(right: 6),
                                  decoration: BoxDecoration(
                                    color: Colors.green.withValues(alpha: 0.15),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text('RTF: ${rtf}x',
                                      style: const TextStyle(fontSize: 11, color: Colors.greenAccent)),
                                ),
                              if (rss != null)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                                  decoration: BoxDecoration(
                                    color: Colors.blue.withValues(alpha: 0.15),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text('RSS: $rss MB',
                                      style: const TextStyle(fontSize: 11, color: Colors.blueAccent)),
                                ),
                            ],
                          ),
                        ),
                      AudioPlayerWidget(filePath: file.path, key: ValueKey(file.path)),
                    ],
                  ),
                ),
              );
            }),
          ],
        ],
      ),
    );
  }

  // --- REUSABLE SECTION CARD ---
  Widget _buildSectionCard({
    required String stepNumber,
    required String title,
    required String subtitle,
    required Widget child,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Container(
                  width: 26,
                  height: 26,
                  alignment: Alignment.center,
                  decoration: const BoxDecoration(
                    color: Colors.deepPurple,
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    stepNumber,
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13.5, color: Colors.white),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          fontSize: 15.5,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Padding(
              padding: const EdgeInsets.only(left: 34, bottom: 10),
              child: Text(
                subtitle,
                style: TextStyle(
                  fontSize: 13.5,
                  color: Colors.white.withValues(alpha: 0.7),
                  height: 1.35,
                ),
              ),
            ),
            const Divider(height: 1, color: Colors.white12),
            const SizedBox(height: 10),
            child,
          ],
        ),
      ),
    );
  }
}
