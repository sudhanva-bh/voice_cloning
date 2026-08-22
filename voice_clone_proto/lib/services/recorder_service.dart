import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';

class RecorderService {
  final _recorder = AudioRecorder();

  Future<void> start() async {
    if (!await Permission.microphone.request().isGranted) {
      throw StateError('Microphone permission denied');
    }
    final dir = await getApplicationDocumentsDirectory();
    final path = '${dir.path}/reference_clip.wav';
    await _recorder.start(
      const RecordConfig(encoder: AudioEncoder.wav, sampleRate: 24000, numChannels: 1),
      path: path,
    );
  }

  Future<String?> stop() => _recorder.stop();
}
