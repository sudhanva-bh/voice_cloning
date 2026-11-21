import 'package:ffmpeg_kit_flutter_new_audio/ffmpeg_kit.dart';
import 'package:ffmpeg_kit_flutter_new_audio/return_code.dart';
import 'package:path_provider/path_provider.dart';

class AudioConverter {
  static Future<String?> convertToWav(String inputPath) async {
    final dir = await getTemporaryDirectory();
    final outPath = '${dir.path}/converted_${DateTime.now().millisecondsSinceEpoch}.wav';
    
    // Convert to 16-bit PCM WAV at 24kHz (required by sherpa-onnx)
    final command = '-y -i "$inputPath" -acodec pcm_s16le -ar 24000 -ac 1 "$outPath"';
    final session = await FFmpegKit.execute(command);
    final returnCode = await session.getReturnCode();
    
    if (ReturnCode.isSuccess(returnCode)) {
      return outPath;
    }
    
    final logs = await session.getLogsAsString();
    print('FFmpeg convertToWav failed: $logs');
    return null;
  }

  static Future<String?> convertFormat(String inputPath, String format) async {
    if (format.toLowerCase() == 'wav') return inputPath;
    
    final dir = await getTemporaryDirectory();
    final ext = format.toLowerCase();
    final outPath = '${dir.path}/export_${DateTime.now().millisecondsSinceEpoch}.$ext';
    
    final command = '-y -i "$inputPath" "$outPath"';
    final session = await FFmpegKit.execute(command);
    final returnCode = await session.getReturnCode();
    
    if (ReturnCode.isSuccess(returnCode)) {
      return outPath;
    }
    
    final logs = await session.getLogsAsString();
    print('FFmpeg convertFormat failed: $logs');
    return null;
  }
}
