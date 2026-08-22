import 'dart:io';
import 'package:flutter/services.dart' show rootBundle, AssetManifest;
import 'package:path_provider/path_provider.dart';

class ModelLoader {
  static const _files = [
    'zipvoice/encoder.int8.onnx',
    'zipvoice/decoder.int8.onnx',
    'zipvoice/tokens.txt',
    'zipvoice/lexicon.txt',
    'zipvoice/vocos_24khz.onnx',
  ];

  static Future<String> ensureModelsOnDisk() async {
    final dir = await getApplicationSupportDirectory();
    final modelDir = Directory('${dir.path}/zipvoice');
    if (!await modelDir.exists()) await modelDir.create(recursive: true);

    for (final assetPath in _files) {
      final outFile = File('${dir.path}/$assetPath');
      if (await outFile.exists()) continue;
      await outFile.parent.create(recursive: true);
      final bytes = await rootBundle.load('assets/$assetPath');
      await outFile.writeAsBytes(bytes.buffer.asUint8List());
    }

    // espeak-ng-data is a folder of many files — copy via AssetManifest
    final manifest = await AssetManifest.loadFromAssetBundle(rootBundle);
    final assetPaths = manifest.listAssets()
        .where((path) => path.startsWith('assets/zipvoice/espeak-ng-data/'));
    for (final path in assetPaths) {
      final relative = path.replaceFirst('assets/', '');
      final outFile = File('${dir.path}/$relative');
      if (await outFile.exists()) continue;
      await outFile.parent.create(recursive: true);
      final bytes = await rootBundle.load(path);
      await outFile.writeAsBytes(bytes.buffer.asUint8List());
    }

    return modelDir.path;
  }
}
