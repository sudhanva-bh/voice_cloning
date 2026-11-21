import 'dart:io';
import 'dart:isolate';
import 'package:sherpa_onnx/sherpa_onnx.dart' as sherpa_onnx;
import 'model_loader.dart';

class TtsService {
  String? _modelDir;

  Future<void> init() async {
    sherpa_onnx.initBindings();
    _modelDir = await ModelLoader.ensureModelsOnDisk();
  }

  Future<({String path, double rtf, int rssMB})> generate({
    required String referenceWavPath,
    required String referenceText,
    required String targetText,
    required String outputWavPath,
    int numSteps = 4,
  }) async {
    if (_modelDir == null) throw StateError('Call init() first');
    
    final modelDir = _modelDir!;

    return await Isolate.run(() {
      sherpa_onnx.initBindings();

      final config = sherpa_onnx.OfflineTtsConfig(
        model: sherpa_onnx.OfflineTtsModelConfig(
          zipvoice: sherpa_onnx.OfflineTtsZipVoiceModelConfig(
            encoder: '$modelDir/encoder.int8.onnx',
            decoder: '$modelDir/decoder.int8.onnx',
            tokens: '$modelDir/tokens.txt',
            lexicon: '$modelDir/lexicon.txt',
            dataDir: '$modelDir/espeak-ng-data',
            vocoder: '$modelDir/vocos_24khz.onnx',
          ),
          numThreads: 2,
          debug: false,
          provider: 'cpu',
        ),
      );

      final tts = sherpa_onnx.OfflineTts(config);

      final startTime = DateTime.now();

      final wave = sherpa_onnx.readWave(referenceWavPath);
      final audio = tts.generateWithConfig(
        text: targetText,
        config: sherpa_onnx.OfflineTtsGenerationConfig(
          referenceAudio: wave.samples,
          referenceSampleRate: wave.sampleRate,
          referenceText: referenceText,
          numSteps: numSteps,
        ),
      );

      final elapsed = DateTime.now().difference(startTime).inMilliseconds / 1000.0;
      final duration = audio.samples.length / audio.sampleRate;
      final rtf = elapsed / duration;

      sherpa_onnx.writeWave(
        filename: outputWavPath,
        samples: audio.samples,
        sampleRate: audio.sampleRate,
      );

      int rssMB = 0;
      try {
        final file = File('/proc/self/status');
        if (file.existsSync()) {
          for (final line in file.readAsLinesSync()) {
            if (line.startsWith('VmRSS:')) {
              final parts = line.split(RegExp(r'\s+'));
              if (parts.length >= 2) {
                rssMB = (int.tryParse(parts[1]) ?? 0) ~/ 1024;
                break;
              }
            }
          }
        }
      } catch (_) {}

      tts.free();
      return (path: outputWavPath, rtf: rtf, rssMB: rssMB);
    });
  }
}
