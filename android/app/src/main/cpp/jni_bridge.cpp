#include <jni.h>
#include <string>
#include <vector>
#include <android/log.h>
#include "litert_indic_engine.h"

#define TAG "LiteRTIndicNative"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

extern "C" {

JNIEXPORT jlong JNICALL
Java_com_indic_voice_LiteRTIndicEngine_nativeInit(
    JNIEnv* env,
    jobject /* thiz */,
    jobject dit_buffer,
    jlong dit_size,
    jobject vocos_buffer,
    jlong vocos_size,
    jstring vocab_str,
    jint num_threads
) {
    const void* dit_data = env->GetDirectBufferAddress(dit_buffer);
    const void* vocos_data = env->GetDirectBufferAddress(vocos_buffer);

    if (!dit_data || !vocos_data) {
        LOGE("Failed to get direct buffer addresses for models");
        return 0;
    }

    const char* vocab_cstr = env->GetStringUTFChars(vocab_str, nullptr);
    jsize vocab_len = env->GetStringUTFLength(vocab_str);

    auto* engine = new indic::LiteRTIndicEngine();
    bool success = engine->initialize(
        dit_data, static_cast<size_t>(dit_size),
        vocos_data, static_cast<size_t>(vocos_size),
        vocab_cstr, static_cast<size_t>(vocab_len),
        num_threads
    );

    env->ReleaseStringUTFChars(vocab_str, vocab_cstr);

    if (!success) {
        LOGE("Failed to initialize LiteRT Indic Engine");
        delete engine;
        return 0;
    }

    LOGI("LiteRT Indic Engine initialized successfully with %d threads", num_threads);
    return reinterpret_cast<jlong>(engine);
}

JNIEXPORT jlong JNICALL
Java_com_indic_voice_LiteRTIndicEngine_nativeInitFromFile(
    JNIEnv* env,
    jobject /* thiz */,
    jstring dit_path_str,
    jstring vocos_path_str,
    jstring vocab_path_str,
    jint num_threads
) {
    const char* dit_cstr = env->GetStringUTFChars(dit_path_str, nullptr);
    const char* vocos_cstr = env->GetStringUTFChars(vocos_path_str, nullptr);
    const char* vocab_cstr = env->GetStringUTFChars(vocab_path_str, nullptr);

    std::string dit_path(dit_cstr);
    std::string vocos_path(vocos_cstr);
    std::string vocab_path(vocab_cstr);

    env->ReleaseStringUTFChars(dit_path_str, dit_cstr);
    env->ReleaseStringUTFChars(vocos_path_str, vocos_cstr);
    env->ReleaseStringUTFChars(vocab_path_str, vocab_cstr);

    auto* engine = new indic::LiteRTIndicEngine();
    bool success = engine->initializeFromFiles(
        dit_path,
        vocos_path,
        vocab_path,
        num_threads
    );

    if (!success) {
        LOGE("Failed to initialize LiteRT Indic Engine from files");
        delete engine;
        return 0;
    }

    LOGI("LiteRT Indic Engine initialized from files successfully with %d threads", num_threads);
    return reinterpret_cast<jlong>(engine);
}


JNIEXPORT jfloatArray JNICALL
Java_com_indic_voice_LiteRTIndicEngine_nativeSynthesize(
    JNIEnv* env,
    jobject /* thiz */,
    jlong engine_ptr,
    jfloatArray ref_pcm_array,
    jstring ref_text_str,
    jstring target_text_str,
    jint num_steps,
    jfloat cfg_strength,
    jint seed,
    jfloatArray out_telemetry_array
) {
    auto* engine = reinterpret_cast<indic::LiteRTIndicEngine*>(engine_ptr);
    if (!engine || !engine->isReady()) {
        LOGE("Engine pointer is invalid or not ready");
        return nullptr;
    }

    jsize pcm_len = env->GetArrayLength(ref_pcm_array);
    jfloat* pcm_elements = env->GetFloatArrayElements(ref_pcm_array, nullptr);

    const char* ref_cstr = env->GetStringUTFChars(ref_text_str, nullptr);
    const char* target_cstr = env->GetStringUTFChars(target_text_str, nullptr);

    std::string ref_text(ref_cstr);
    std::string target_text(target_cstr);

    env->ReleaseStringUTFChars(ref_text_str, ref_cstr);
    env->ReleaseStringUTFChars(target_text_str, target_cstr);

    indic::EngineTelemetry telemetry{};
    std::vector<float> audio_out = engine->synthesize(
        pcm_elements, static_cast<size_t>(pcm_len),
        ref_text, target_text,
        num_steps, cfg_strength, static_cast<uint32_t>(seed),
        &telemetry
    );

    env->ReleaseFloatArrayElements(ref_pcm_array, pcm_elements, JNI_ABORT);

    // Populate telemetry: [0]=mel_ms, [1]=diff_ms, [2]=voc_ms, [3]=istft_ms, [4]=total_ms, [5]=dur_sec, [6]=rtf
    if (out_telemetry_array) {
        jfloat telem_data[7] = {
            telemetry.mel_extract_time_ms,
            telemetry.diffusion_time_ms,
            telemetry.vocos_time_ms,
            telemetry.istft_time_ms,
            telemetry.total_time_ms,
            telemetry.audio_duration_sec,
            telemetry.real_time_factor
        };
        env->SetFloatArrayRegion(out_telemetry_array, 0, 7, telem_data);
    }

    jfloatArray result = env->NewFloatArray(audio_out.size());
    if (!audio_out.empty()) {
        env->SetFloatArrayRegion(result, 0, audio_out.size(), audio_out.data());
    }

    return result;
}

JNIEXPORT jfloatArray JNICALL
Java_com_indic_voice_LiteRTIndicEngine_nativeDecodeWav(
    JNIEnv* env,
    jclass /* clazz */,
    jbyteArray wav_bytes_array
) {
    jsize len = env->GetArrayLength(wav_bytes_array);
    jbyte* bytes = env->GetByteArrayElements(wav_bytes_array, nullptr);

    int sr = 24000;
    std::vector<float> samples = indic::AudioProcessor::decodeWavBytes(
        reinterpret_cast<const uint8_t*>(bytes), static_cast<size_t>(len), &sr
    );

    env->ReleaseByteArrayElements(wav_bytes_array, bytes, JNI_ABORT);

    jfloatArray result = env->NewFloatArray(samples.size());
    if (!samples.empty()) {
        env->SetFloatArrayRegion(result, 0, samples.size(), samples.data());
    }
    return result;
}

JNIEXPORT void JNICALL
Java_com_indic_voice_LiteRTIndicEngine_nativeDestroy(
    JNIEnv* /* env */,
    jobject /* thiz */,
    jlong engine_ptr
) {
    auto* engine = reinterpret_cast<indic::LiteRTIndicEngine*>(engine_ptr);
    if (engine) {
        delete engine;
        LOGI("LiteRT Indic Engine destroyed");
    }
}

} // extern "C"
