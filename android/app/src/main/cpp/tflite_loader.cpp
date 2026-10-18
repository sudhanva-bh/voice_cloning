#include <dlfcn.h>
#include <cstring>
#include <android/log.h>
#include "tensorflow/lite/c/c_api.h"
#include "tensorflow/lite/delegates/xnnpack/xnnpack_delegate.h"

#define TAG "TfLiteLoader"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN, TAG, __VA_ARGS__)
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
typedef TfLiteStatus (*fn_TfLiteInterpreterModifyGraphWithDelegate)(TfLiteInterpreter*, TfLiteDelegate*);

typedef int32_t (*fn_TfLiteInterpreterGetInputTensorCount)(const TfLiteInterpreter*);
typedef TfLiteTensor* (*fn_TfLiteInterpreterGetInputTensor)(const TfLiteInterpreter*, int32_t);
typedef TfLiteStatus (*fn_TfLiteInterpreterResizeInputTensor)(TfLiteInterpreter*, int32_t, const int*, int32_t);
typedef TfLiteStatus (*fn_TfLiteInterpreterAllocateTensors)(TfLiteInterpreter*);
typedef TfLiteStatus (*fn_TfLiteInterpreterInvoke)(TfLiteInterpreter*);
typedef TfLiteStatus (*fn_TfLiteInterpreterResetVariableTensors)(TfLiteInterpreter*);

typedef int32_t (*fn_TfLiteInterpreterGetOutputTensorCount)(const TfLiteInterpreter*);
typedef const TfLiteTensor* (*fn_TfLiteInterpreterGetOutputTensor)(const TfLiteInterpreter*, int32_t);
typedef const TfLiteTensor* (*fn_TfLiteInterpreterGetTensor)(const TfLiteInterpreter*, int32_t);
typedef int32_t (*fn_TfLiteInterpreterGetInputTensorIndex)(const TfLiteInterpreter*, int32_t);
typedef int32_t (*fn_TfLiteOpaqueTensorGetAllocationType)(const TfLiteTensor*);

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

typedef TfLiteSignatureRunner* (*fn_TfLiteInterpreterGetSignatureRunner)(const TfLiteInterpreter*, const char*);
typedef int32_t (*fn_TfLiteSignatureRunnerGetInputCount)(const TfLiteSignatureRunner*);
typedef const char* (*fn_TfLiteSignatureRunnerGetInputName)(const TfLiteSignatureRunner*, int32_t);
typedef int32_t (*fn_TfLiteSignatureRunnerGetOutputCount)(const TfLiteSignatureRunner*);
typedef const char* (*fn_TfLiteSignatureRunnerGetOutputName)(const TfLiteSignatureRunner*, int32_t);
typedef TfLiteStatus (*fn_TfLiteSignatureRunnerResizeInputTensor)(TfLiteSignatureRunner*, const char*, const int*, int32_t);
typedef TfLiteStatus (*fn_TfLiteSignatureRunnerAllocateTensors)(TfLiteSignatureRunner*);
typedef TfLiteTensor* (*fn_TfLiteSignatureRunnerGetInputTensor)(TfLiteSignatureRunner*, const char*);
typedef const TfLiteTensor* (*fn_TfLiteSignatureRunnerGetOutputTensor)(TfLiteSignatureRunner*, const char*);
typedef TfLiteStatus (*fn_TfLiteSignatureRunnerInvoke)(TfLiteSignatureRunner*);
typedef void (*fn_TfLiteSignatureRunnerDelete)(TfLiteSignatureRunner*);

static void* g_tflite_handle = nullptr;

static fn_TfLiteModelCreate p_TfLiteModelCreate = nullptr;
static fn_TfLiteModelCreateFromFile p_TfLiteModelCreateFromFile = nullptr;
static fn_TfLiteModelDelete p_TfLiteModelDelete = nullptr;
static fn_TfLiteInterpreterOptionsCreate p_TfLiteInterpreterOptionsCreate = nullptr;
static fn_TfLiteInterpreterOptionsDelete p_TfLiteInterpreterOptionsDelete = nullptr;
static fn_TfLiteInterpreterOptionsSetNumThreads p_TfLiteInterpreterOptionsSetNumThreads = nullptr;
static fn_TfLiteInterpreterOptionsAddDelegate p_TfLiteInterpreterOptionsAddDelegate = nullptr;
static fn_TfLiteInterpreterCreate p_TfLiteInterpreterCreate = nullptr;
static fn_TfLiteInterpreterDelete p_TfLiteInterpreterDelete = nullptr;
static fn_TfLiteInterpreterModifyGraphWithDelegate p_TfLiteInterpreterModifyGraphWithDelegate = nullptr;
static fn_TfLiteInterpreterResizeInputTensor p_TfLiteInterpreterResizeInputTensor = nullptr;
static fn_TfLiteInterpreterAllocateTensors p_TfLiteInterpreterAllocateTensors = nullptr;
static fn_TfLiteInterpreterInvoke p_TfLiteInterpreterInvoke = nullptr;
static fn_TfLiteInterpreterResetVariableTensors p_TfLiteInterpreterResetVariableTensors = nullptr;
static fn_TfLiteInterpreterGetInputTensorCount p_TfLiteInterpreterGetInputTensorCount = nullptr;
static fn_TfLiteInterpreterGetInputTensor p_TfLiteInterpreterGetInputTensor = nullptr;
static fn_TfLiteInterpreterGetOutputTensorCount p_TfLiteInterpreterGetOutputTensorCount = nullptr;
static fn_TfLiteInterpreterGetOutputTensor p_TfLiteInterpreterGetOutputTensor = nullptr;
static fn_TfLiteInterpreterGetTensor p_TfLiteInterpreterGetTensor = nullptr;
static fn_TfLiteInterpreterGetInputTensorIndex p_TfLiteInterpreterGetInputTensorIndex = nullptr;
static fn_TfLiteOpaqueTensorGetAllocationType p_TfLiteOpaqueTensorGetAllocationType = nullptr;
static fn_TfLiteTensorName p_TfLiteTensorName = nullptr;
static fn_TfLiteTensorByteSize p_TfLiteTensorByteSize = nullptr;
static fn_TfLiteTensorType p_TfLiteTensorType = nullptr;
static fn_TfLiteTensorNumDims p_TfLiteTensorNumDims = nullptr;
static fn_TfLiteTensorDim p_TfLiteTensorDim = nullptr;
static fn_TfLiteTensorData p_TfLiteTensorData = nullptr;
static fn_TfLiteTensorCopyFromBuffer p_TfLiteTensorCopyFromBuffer = nullptr;
static fn_TfLiteTensorCopyToBuffer p_TfLiteTensorCopyToBuffer = nullptr;
static fn_TfLiteXNNPackDelegateOptionsDefault p_TfLiteXNNPackDelegateOptionsDefault = nullptr;
static fn_TfLiteXNNPackDelegateCreate p_TfLiteXNNPackDelegateCreate = nullptr;
static fn_TfLiteXNNPackDelegateDelete p_TfLiteXNNPackDelegateDelete = nullptr;

static fn_TfLiteInterpreterGetSignatureRunner p_TfLiteInterpreterGetSignatureRunner = nullptr;
static fn_TfLiteSignatureRunnerGetInputCount p_TfLiteSignatureRunnerGetInputCount = nullptr;
static fn_TfLiteSignatureRunnerGetInputName p_TfLiteSignatureRunnerGetInputName = nullptr;
static fn_TfLiteSignatureRunnerGetOutputCount p_TfLiteSignatureRunnerGetOutputCount = nullptr;
static fn_TfLiteSignatureRunnerGetOutputName p_TfLiteSignatureRunnerGetOutputName = nullptr;
static fn_TfLiteSignatureRunnerResizeInputTensor p_TfLiteSignatureRunnerResizeInputTensor = nullptr;
static fn_TfLiteSignatureRunnerAllocateTensors p_TfLiteSignatureRunnerAllocateTensors = nullptr;
static fn_TfLiteSignatureRunnerGetInputTensor p_TfLiteSignatureRunnerGetInputTensor = nullptr;
static fn_TfLiteSignatureRunnerGetOutputTensor p_TfLiteSignatureRunnerGetOutputTensor = nullptr;
static fn_TfLiteSignatureRunnerInvoke p_TfLiteSignatureRunnerInvoke = nullptr;
static fn_TfLiteSignatureRunnerDelete p_TfLiteSignatureRunnerDelete = nullptr;

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
    BIND_SYM(TfLiteModelCreateFromFile);
    BIND_SYM(TfLiteModelDelete);
    BIND_SYM(TfLiteInterpreterOptionsCreate);
    BIND_SYM(TfLiteInterpreterOptionsDelete);
    BIND_SYM(TfLiteInterpreterOptionsSetNumThreads);
    BIND_SYM(TfLiteInterpreterOptionsAddDelegate);
    BIND_SYM(TfLiteInterpreterCreate);
    BIND_SYM(TfLiteInterpreterDelete);
    BIND_SYM(TfLiteInterpreterModifyGraphWithDelegate);
    BIND_SYM(TfLiteInterpreterResizeInputTensor);
    BIND_SYM(TfLiteInterpreterAllocateTensors);
    BIND_SYM(TfLiteInterpreterInvoke);
    BIND_SYM(TfLiteInterpreterResetVariableTensors);
    BIND_SYM(TfLiteInterpreterGetInputTensorCount);
    BIND_SYM(TfLiteInterpreterGetInputTensor);
    BIND_SYM(TfLiteInterpreterGetOutputTensorCount);
    BIND_SYM(TfLiteInterpreterGetOutputTensor);
    BIND_SYM(TfLiteInterpreterGetTensor);
    BIND_SYM(TfLiteInterpreterGetInputTensorIndex);
    BIND_SYM(TfLiteOpaqueTensorGetAllocationType);
    BIND_SYM(TfLiteTensorName);
    BIND_SYM(TfLiteTensorByteSize);
    BIND_SYM(TfLiteTensorType);
    BIND_SYM(TfLiteTensorNumDims);
    BIND_SYM(TfLiteTensorDim);
    BIND_SYM(TfLiteTensorData);
    BIND_SYM(TfLiteTensorCopyFromBuffer);
    BIND_SYM(TfLiteTensorCopyToBuffer);
    BIND_SYM(TfLiteInterpreterGetSignatureRunner);
    BIND_SYM(TfLiteSignatureRunnerGetInputCount);
    BIND_SYM(TfLiteSignatureRunnerGetInputName);
    BIND_SYM(TfLiteSignatureRunnerGetOutputCount);
    BIND_SYM(TfLiteSignatureRunnerGetOutputName);
    BIND_SYM(TfLiteSignatureRunnerResizeInputTensor);
    BIND_SYM(TfLiteSignatureRunnerAllocateTensors);
    BIND_SYM(TfLiteSignatureRunnerGetInputTensor);
    BIND_SYM(TfLiteSignatureRunnerGetOutputTensor);
    BIND_SYM(TfLiteSignatureRunnerInvoke);
    BIND_SYM(TfLiteSignatureRunnerDelete);
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

TfLiteModel* TfLiteModelCreateFromFile(const char* model_path) {
    ensure_tflite_loaded();
    return p_TfLiteModelCreateFromFile ? p_TfLiteModelCreateFromFile(model_path) : nullptr;
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

TfLiteStatus TfLiteInterpreterModifyGraphWithDelegate(TfLiteInterpreter* interpreter, TfLiteDelegate* delegate) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterModifyGraphWithDelegate
        ? p_TfLiteInterpreterModifyGraphWithDelegate(interpreter, delegate)
        : kTfLiteError;
}

TfLiteStatus TfLiteInterpreterResizeInputTensor(
    TfLiteInterpreter* interpreter,
    int32_t input_index,
    const int* input_dims,
    int32_t input_dims_size
) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterResizeInputTensor
        ? p_TfLiteInterpreterResizeInputTensor(interpreter, input_index, input_dims, input_dims_size)
        : kTfLiteError;
}

TfLiteStatus TfLiteInterpreterAllocateTensors(TfLiteInterpreter* interpreter) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterAllocateTensors ? p_TfLiteInterpreterAllocateTensors(interpreter) : kTfLiteError;
}

TfLiteStatus TfLiteInterpreterInvoke(TfLiteInterpreter* interpreter) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterInvoke ? p_TfLiteInterpreterInvoke(interpreter) : kTfLiteError;
}

TfLiteStatus TfLiteInterpreterResetVariableTensors(TfLiteInterpreter* interpreter) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterResetVariableTensors ? p_TfLiteInterpreterResetVariableTensors(interpreter) : kTfLiteError;
}

int32_t TfLiteInterpreterGetInputTensorCount(const TfLiteInterpreter* interpreter) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterGetInputTensorCount ? p_TfLiteInterpreterGetInputTensorCount(interpreter) : 0;
}

TfLiteTensor* TfLiteInterpreterGetInputTensor(const TfLiteInterpreter* interpreter, int32_t input_index) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterGetInputTensor ? p_TfLiteInterpreterGetInputTensor(interpreter, input_index) : nullptr;
}

int32_t TfLiteInterpreterGetOutputTensorCount(const TfLiteInterpreter* interpreter) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterGetOutputTensorCount ? p_TfLiteInterpreterGetOutputTensorCount(interpreter) : 0;
}

const TfLiteTensor* TfLiteInterpreterGetOutputTensor(const TfLiteInterpreter* interpreter, int32_t output_index) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterGetOutputTensor ? p_TfLiteInterpreterGetOutputTensor(interpreter, output_index) : nullptr;
}

const TfLiteTensor* TfLiteInterpreterGetTensor(const TfLiteInterpreter* interpreter, int32_t tensor_index) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterGetTensor ? p_TfLiteInterpreterGetTensor(interpreter, tensor_index) : nullptr;
}

int32_t TfLiteInterpreterGetInputTensorIndex(const TfLiteInterpreter* interpreter, int32_t input_index) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterGetInputTensorIndex ? p_TfLiteInterpreterGetInputTensorIndex(interpreter, input_index) : -1;
}

int32_t TfLiteOpaqueTensorGetAllocationType(const TfLiteTensor* tensor) {
    ensure_tflite_loaded();
    return p_TfLiteOpaqueTensorGetAllocationType ? p_TfLiteOpaqueTensorGetAllocationType(tensor) : -1;
}

const char* TfLiteTensorName(const TfLiteTensor* tensor) {
    ensure_tflite_loaded();
    return p_TfLiteTensorName ? p_TfLiteTensorName(tensor) : "";
}

size_t TfLiteTensorByteSize(const TfLiteTensor* tensor) {
    ensure_tflite_loaded();
    return p_TfLiteTensorByteSize ? p_TfLiteTensorByteSize(tensor) : 0;
}

TfLiteType TfLiteTensorType(const TfLiteTensor* tensor) {
    ensure_tflite_loaded();
    return p_TfLiteTensorType ? p_TfLiteTensorType(tensor) : kTfLiteNoType;
}

int32_t TfLiteTensorNumDims(const TfLiteTensor* tensor) {
    ensure_tflite_loaded();
    return p_TfLiteTensorNumDims ? p_TfLiteTensorNumDims(tensor) : 0;
}

int32_t TfLiteTensorDim(const TfLiteTensor* tensor, int32_t dim_index) {
    ensure_tflite_loaded();
    return p_TfLiteTensorDim ? p_TfLiteTensorDim(tensor, dim_index) : 0;
}

void* TfLiteTensorData(const TfLiteTensor* tensor) {
    ensure_tflite_loaded();
    return p_TfLiteTensorData ? p_TfLiteTensorData(tensor) : nullptr;
}

TfLiteStatus TfLiteTensorCopyFromBuffer(TfLiteTensor* tensor, const void* input_data, size_t input_data_size) {
    if (!tensor || !input_data) return kTfLiteError;
    void* dst = TfLiteTensorData(tensor);
    if (dst && input_data_size > 0) {
        std::memcpy(dst, input_data, input_data_size);
        return kTfLiteOk;
    }
    return kTfLiteError;
}

TfLiteStatus TfLiteTensorCopyToBuffer(const TfLiteTensor* tensor, void* output_data, size_t output_data_size) {
    if (!tensor || !output_data) return kTfLiteError;
    const void* src = TfLiteTensorData(tensor);
    if (src && output_data_size > 0) {
        std::memcpy(output_data, src, output_data_size);
        return kTfLiteOk;
    }
    return kTfLiteError;
}

TfLiteXNNPackDelegateOptions TfLiteXNNPackDelegateOptionsDefault(void) {
    ensure_tflite_loaded();
    if (p_TfLiteXNNPackDelegateOptionsDefault) {
        return p_TfLiteXNNPackDelegateOptionsDefault();
    }
    TfLiteXNNPackDelegateOptions opt{};
    opt.num_threads = 5;
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

TfLiteSignatureRunner* TfLiteInterpreterGetSignatureRunner(const TfLiteInterpreter* interpreter, const char* signature_key) {
    ensure_tflite_loaded();
    return p_TfLiteInterpreterGetSignatureRunner ? p_TfLiteInterpreterGetSignatureRunner(interpreter, signature_key) : nullptr;
}

int32_t TfLiteSignatureRunnerGetInputCount(const TfLiteSignatureRunner* runner) {
    ensure_tflite_loaded();
    return p_TfLiteSignatureRunnerGetInputCount ? p_TfLiteSignatureRunnerGetInputCount(runner) : 0;
}

const char* TfLiteSignatureRunnerGetInputName(const TfLiteSignatureRunner* runner, int32_t input_index) {
    ensure_tflite_loaded();
    return p_TfLiteSignatureRunnerGetInputName ? p_TfLiteSignatureRunnerGetInputName(runner, input_index) : "";
}

int32_t TfLiteSignatureRunnerGetOutputCount(const TfLiteSignatureRunner* runner) {
    ensure_tflite_loaded();
    return p_TfLiteSignatureRunnerGetOutputCount ? p_TfLiteSignatureRunnerGetOutputCount(runner) : 0;
}

const char* TfLiteSignatureRunnerGetOutputName(const TfLiteSignatureRunner* runner, int32_t output_index) {
    ensure_tflite_loaded();
    return p_TfLiteSignatureRunnerGetOutputName ? p_TfLiteSignatureRunnerGetOutputName(runner, output_index) : "";
}

TfLiteStatus TfLiteSignatureRunnerResizeInputTensor(
    TfLiteSignatureRunner* runner,
    const char* input_name,
    const int* input_dims,
    int32_t input_dims_size
) {
    ensure_tflite_loaded();
    return p_TfLiteSignatureRunnerResizeInputTensor
        ? p_TfLiteSignatureRunnerResizeInputTensor(runner, input_name, input_dims, input_dims_size)
        : kTfLiteError;
}

TfLiteStatus TfLiteSignatureRunnerAllocateTensors(TfLiteSignatureRunner* runner) {
    ensure_tflite_loaded();
    return p_TfLiteSignatureRunnerAllocateTensors ? p_TfLiteSignatureRunnerAllocateTensors(runner) : kTfLiteError;
}

TfLiteTensor* TfLiteSignatureRunnerGetInputTensor(TfLiteSignatureRunner* runner, const char* input_name) {
    ensure_tflite_loaded();
    return p_TfLiteSignatureRunnerGetInputTensor ? p_TfLiteSignatureRunnerGetInputTensor(runner, input_name) : nullptr;
}

const TfLiteTensor* TfLiteSignatureRunnerGetOutputTensor(TfLiteSignatureRunner* runner, const char* output_name) {
    ensure_tflite_loaded();
    return p_TfLiteSignatureRunnerGetOutputTensor ? p_TfLiteSignatureRunnerGetOutputTensor(runner, output_name) : nullptr;
}

TfLiteStatus TfLiteSignatureRunnerInvoke(TfLiteSignatureRunner* runner) {
    ensure_tflite_loaded();
    return p_TfLiteSignatureRunnerInvoke ? p_TfLiteSignatureRunnerInvoke(runner) : kTfLiteError;
}

void TfLiteSignatureRunnerDelete(TfLiteSignatureRunner* runner) {
    ensure_tflite_loaded();
    if (p_TfLiteSignatureRunnerDelete) p_TfLiteSignatureRunnerDelete(runner);
}

} // extern "C"
