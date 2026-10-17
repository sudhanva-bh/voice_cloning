#include <dlfcn.h>
#include <android/log.h>
#include "tensorflow/lite/c/c_api.h"
#include "tensorflow/lite/delegates/xnnpack/xnnpack_delegate.h"

#define TAG "TfLiteLoader"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

// Function pointer definitions
typedef const char* (*fn_TfLiteVersion)(void);
typedef TfLiteModel* (*fn_TfLiteModelCreate)(const void*, size_t);
typedef TfLiteModel* (*fn_TfLiteModelCreateFromFile)(const char*);
typedef void (*fn_TfLiteModelDelete)(TfLiteModel*);

typedef TfLiteInterpreterOptions* (*fn_TfLiteInterpreterOptionsCreate)(void);
typedef void (*fn_TfLiteInterpreterOptionsDelete)(TfLiteInterpreterOptions*);
typedef void (*fn_TfLiteInterpreterOptionsSetNumThreads)(TfLiteInterpreterOptions*, int32_t);
typedef void (*fn_TfLiteInterpreterOptionsAddDelegate)(TfLiteInterpreterOptions*, TfLiteDelegate*);

typedef TfLiteInterpreter* (*fn_TfLiteInterpreterCreate)(const TfLiteModel*, const TfLiteInterpreterOptions*);
typedef void (*fn_TfLiteInterpreterDelete)(TfLiteInterpreter*);

typedef int32_t (*fn_TfLiteInterpreterGetInputTensorCount)(const TfLiteInterpreter*);
typedef TfLiteTensor* (*fn_TfLiteInterpreterGetInputTensor)(const TfLiteInterpreter*, int32_t);
typedef TfLiteStatus (*fn_TfLiteInterpreterResizeInputTensor)(TfLiteInterpreter*, int32_t, const int*, int32_t);
typedef TfLiteStatus (*fn_TfLiteInterpreterAllocateTensors)(TfLiteInterpreter*);
typedef TfLiteStatus (*fn_TfLiteInterpreterInvoke)(TfLiteInterpreter*);

typedef int32_t (*fn_TfLiteInterpreterGetOutputTensorCount)(const TfLiteInterpreter*);
typedef const TfLiteTensor* (*fn_TfLiteInterpreterGetOutputTensor)(const TfLiteInterpreter*, int32_t);

typedef TfLiteType (*fn_TfLiteTensorType)(const TfLiteTensor*);
typedef int32_t (*fn_TfLiteTensorNumDims)(const TfLiteTensor*);
typedef int32_t (*fn_TfLiteTensorDim)(const TfLiteTensor*, int32_t);
typedef size_t (*fn_TfLiteTensorByteSize)(const TfLiteTensor*);
typedef void* (*fn_TfLiteTensorData)(const TfLiteTensor*);
typedef const char* (*fn_TfLiteTensorName)(const TfLiteTensor*);
typedef TfLiteStatus (*fn_TfLiteTensorCopyFromBuffer)(TfLiteTensor*, const void*, size_t);
typedef TfLiteStatus (*fn_TfLiteTensorCopyToBuffer)(const TfLiteTensor*, void*, size_t);

typedef TfLiteXNNPackDelegateOptions (*fn_TfLiteXNNPackDelegateOptionsDefault)(void);
typedef TfLiteDelegate* (*fn_TfLiteXNNPackDelegateCreate)(const TfLiteXNNPackDelegateOptions*);
typedef void (*fn_TfLiteXNNPackDelegateDelete)(TfLiteDelegate*);

static void* g_tflite_handle = nullptr;

static fn_TfLiteModelCreate p_TfLiteModelCreate = nullptr;
static fn_TfLiteModelDelete p_TfLiteModelDelete = nullptr;
static fn_TfLiteInterpreterOptionsCreate p_TfLiteInterpreterOptionsCreate = nullptr;
static fn_TfLiteInterpreterOptionsDelete p_TfLiteInterpreterOptionsDelete = nullptr;
static fn_TfLiteInterpreterOptionsSetNumThreads p_TfLiteInterpreterOptionsSetNumThreads = nullptr;
static fn_TfLiteInterpreterOptionsAddDelegate p_TfLiteInterpreterOptionsAddDelegate = nullptr;
static fn_TfLiteInterpreterCreate p_TfLiteInterpreterCreate = nullptr;
static fn_TfLiteInterpreterDelete p_TfLiteInterpreterDelete = nullptr;
static fn_TfLiteInterpreterAllocateTensors p_TfLiteInterpreterAllocateTensors = nullptr;
static fn_TfLiteInterpreterInvoke p_TfLiteInterpreterInvoke = nullptr;
static fn_TfLiteInterpreterGetInputTensor p_TfLiteInterpreterGetInputTensor = nullptr;
static fn_TfLiteInterpreterGetOutputTensor p_TfLiteInterpreterGetOutputTensor = nullptr;
static fn_TfLiteTensorData p_TfLiteTensorData = nullptr;
static fn_TfLiteTensorCopyFromBuffer p_TfLiteTensorCopyFromBuffer = nullptr;
static fn_TfLiteTensorCopyToBuffer p_TfLiteTensorCopyToBuffer = nullptr;
static fn_TfLiteXNNPackDelegateOptionsDefault p_TfLiteXNNPackDelegateOptionsDefault = nullptr;
static fn_TfLiteXNNPackDelegateCreate p_TfLiteXNNPackDelegateCreate = nullptr;
static fn_TfLiteXNNPackDelegateDelete p_TfLiteXNNPackDelegateDelete = nullptr;

static void ensure_tflite_loaded() {
    if (g_tflite_handle) return;

    // Try loading libtensorflowlite_jni.so from the app process
    g_tflite_handle = dlopen("libtensorflowlite_jni.so", RTLD_NOW | RTLD_GLOBAL);
    if (!g_tflite_handle) {
        g_tflite_handle = dlopen("libLiteRt.so", RTLD_NOW | RTLD_GLOBAL);
    }
    if (!g_tflite_handle) {
        // Fallback to default symbol table
        g_tflite_handle = RTLD_DEFAULT;
    }

    #define BIND_SYM(name) p_##name = (fn_##name)dlsym(g_tflite_handle, #name)
    BIND_SYM(TfLiteModelCreate);
    BIND_SYM(TfLiteModelDelete);
    BIND_SYM(TfLiteInterpreterOptionsCreate);
    BIND_SYM(TfLiteInterpreterOptionsDelete);
    BIND_SYM(TfLiteInterpreterOptionsSetNumThreads);
    BIND_SYM(TfLiteInterpreterOptionsAddDelegate);
    BIND_SYM(TfLiteInterpreterCreate);
    BIND_SYM(TfLiteInterpreterDelete);
    BIND_SYM(TfLiteInterpreterAllocateTensors);
    BIND_SYM(TfLiteInterpreterInvoke);
    BIND_SYM(TfLiteInterpreterGetInputTensor);
    BIND_SYM(TfLiteInterpreterGetOutputTensor);
    BIND_SYM(TfLiteTensorData);
    BIND_SYM(TfLiteTensorCopyFromBuffer);
    BIND_SYM(TfLiteTensorCopyToBuffer);
    BIND_SYM(TfLiteXNNPackDelegateOptionsDefault);
    BIND_SYM(TfLiteXNNPackDelegateCreate);
    BIND_SYM(TfLiteXNNPackDelegateDelete);
    #undef BIND_SYM

    LOGI("TensorFlow Lite C API symbols bound successfully");
}

extern "C" {

TfLiteModel* TfLiteModelCreate(const void* model_data, size_t model_size) {
    ensure_tflite_loaded();
    return p_TfLiteModelCreate ? p_TfLiteModelCreate(model_data, model_size) : nullptr;
}

void TfLiteModelDelete(TfLiteModel* model) {
    ensure_tflite_loaded();
    if (p_TfLiteModelDelete) p_TfLiteModelDelete(model);
}

TfLiteInterpreterOptions* TfLiteInterpreterOptionsCreate(void) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterOptionsCreate ? p_TfLiteInterpreterOptionsCreate() : nullptr;
}

void TfLiteInterpreterOptionsDelete(TfLiteInterpreterOptions* options) {
    ensure_tflite_loaded();
    if (p_TfLiteInterpreterOptionsDelete) p_TfLiteInterpreterOptionsDelete(options);
}

void TfLiteInterpreterOptionsSetNumThreads(TfLiteInterpreterOptions* options, int32_t num_threads) {
    ensure_tflite_loaded();
    if (p_TfLiteInterpreterOptionsSetNumThreads) p_TfLiteInterpreterOptionsSetNumThreads(options, num_threads);
}

void TfLiteInterpreterOptionsAddDelegate(TfLiteInterpreterOptions* options, TfLiteDelegate* delegate) {
    ensure_tflite_loaded();
    if (p_TfLiteInterpreterOptionsAddDelegate) p_TfLiteInterpreterOptionsAddDelegate(options, delegate);
}

TfLiteInterpreter* TfLiteInterpreterCreate(const TfLiteModel* model, const TfLiteInterpreterOptions* optional_options) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterCreate ? p_TfLiteInterpreterCreate(model, optional_options) : nullptr;
}

void TfLiteInterpreterDelete(TfLiteInterpreter* interpreter) {
    ensure_tflite_loaded();
    if (p_TfLiteInterpreterDelete) p_TfLiteInterpreterDelete(interpreter);
}

TfLiteStatus TfLiteInterpreterAllocateTensors(TfLiteInterpreter* interpreter) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterAllocateTensors ? p_TfLiteInterpreterAllocateTensors(interpreter) : kTfLiteError;
}

TfLiteStatus TfLiteInterpreterInvoke(TfLiteInterpreter* interpreter) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterInvoke ? p_TfLiteInterpreterInvoke(interpreter) : kTfLiteError;
}

TfLiteTensor* TfLiteInterpreterGetInputTensor(const TfLiteInterpreter* interpreter, int32_t input_index) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterGetInputTensor ? p_TfLiteInterpreterGetInputTensor(interpreter, input_index) : nullptr;
}

const TfLiteTensor* TfLiteInterpreterGetOutputTensor(const TfLiteInterpreter* interpreter, int32_t output_index) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterGetOutputTensor ? p_TfLiteInterpreterGetOutputTensor(interpreter, output_index) : nullptr;
}

void* TfLiteTensorData(const TfLiteTensor* tensor) {
    ensure_tflite_loaded();
    return p_TfLiteTensorData ? p_TfLiteTensorData(tensor) : nullptr;
}

TfLiteStatus TfLiteTensorCopyFromBuffer(TfLiteTensor* tensor, const void* input_data, size_t input_data_size) {
    ensure_tflite_loaded();
    return p_TfLiteTensorCopyFromBuffer ? p_TfLiteTensorCopyFromBuffer(tensor, input_data, input_data_size) : kTfLiteError;
}

TfLiteStatus TfLiteTensorCopyToBuffer(const TfLiteTensor* tensor, void* output_data, size_t output_data_size) {
    ensure_tflite_loaded();
    return p_TfLiteTensorCopyToBuffer ? p_TfLiteTensorCopyToBuffer(tensor, output_data, output_data_size) : kTfLiteError;
}

TfLiteXNNPackDelegateOptions TfLiteXNNPackDelegateOptionsDefault(void) {
    ensure_tflite_loaded();
    if (p_TfLiteXNNPackDelegateOptionsDefault) {
        return p_TfLiteXNNPackDelegateOptionsDefault();
    }
    TfLiteXNNPackDelegateOptions opt{};
    opt.num_threads = 4;
    return opt;
}

TfLiteDelegate* TfLiteXNNPackDelegateCreate(const TfLiteXNNPackDelegateOptions* options) {
    ensure_tflite_loaded();
    return p_TfLiteXNNPackDelegateCreate ? p_TfLiteXNNPackDelegateCreate(options) : nullptr;
}

void TfLiteXNNPackDelegateDelete(TfLiteDelegate* delegate) {
    ensure_tflite_loaded();
    if (p_TfLiteXNNPackDelegateDelete) p_TfLiteXNNPackDelegateDelete(delegate);
}

} // extern "C"
