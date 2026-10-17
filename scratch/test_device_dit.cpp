#include <iostream>
#include <vector>
#include <cmath>
#include <cstring>
#include <dlfcn.h>
#include "tensorflow/lite/c/c_api.h"
#include "tensorflow/lite/delegates/xnnpack/xnnpack_delegate.h"

int main() {
    std::cout << "=== STANDALONE DEVICE DIT TEST ===" << std::endl;
    
    // 1. Try loading libtensorflowlite_jni.so
    void* handle = dlopen("libtensorflowlite_jni.so", RTLD_NOW | RTLD_GLOBAL);
    if (!handle) {
        std::cerr << "dlopen failed: " << dlerror() << std::endl;
        return 1;
    }
    std::cout << "libtensorflowlite_jni.so loaded successfully!" << std::endl;

    auto fn_TfLiteModelCreateFromFile = (decltype(&TfLiteModelCreateFromFile))dlsym(handle, "TfLiteModelCreateFromFile");
    auto fn_TfLiteInterpreterOptionsCreate = (decltype(&TfLiteInterpreterOptionsCreate))dlsym(handle, "TfLiteInterpreterOptionsCreate");
    auto fn_TfLiteInterpreterOptionsSetNumThreads = (decltype(&TfLiteInterpreterOptionsSetNumThreads))dlsym(handle, "TfLiteInterpreterOptionsSetNumThreads");
    auto fn_TfLiteInterpreterOptionsAddDelegate = (decltype(&TfLiteInterpreterOptionsAddDelegate))dlsym(handle, "TfLiteInterpreterOptionsAddDelegate");
    auto fn_TfLiteInterpreterOptionsDelete = (decltype(&TfLiteInterpreterOptionsDelete))dlsym(handle, "TfLiteInterpreterOptionsDelete");
    auto fn_TfLiteInterpreterCreate = (decltype(&TfLiteInterpreterCreate))dlsym(handle, "TfLiteInterpreterCreate");
    auto fn_TfLiteInterpreterAllocateTensors = (decltype(&TfLiteInterpreterAllocateTensors))dlsym(handle, "TfLiteInterpreterAllocateTensors");
    auto fn_TfLiteInterpreterInvoke = (decltype(&TfLiteInterpreterInvoke))dlsym(handle, "TfLiteInterpreterInvoke");
    auto fn_TfLiteInterpreterGetInputTensor = (decltype(&TfLiteInterpreterGetInputTensor))dlsym(handle, "TfLiteInterpreterGetInputTensor");
    auto fn_TfLiteInterpreterGetOutputTensor = (decltype(&TfLiteInterpreterGetOutputTensor))dlsym(handle, "TfLiteInterpreterGetOutputTensor");
    auto fn_TfLiteTensorData = (decltype(&TfLiteTensorData))dlsym(handle, "TfLiteTensorData");
    auto fn_TfLiteTensorByteSize = (decltype(&TfLiteTensorByteSize))dlsym(handle, "TfLiteTensorByteSize");
    auto fn_TfLiteXNNPackDelegateOptionsDefault = (decltype(&TfLiteXNNPackDelegateOptionsDefault))dlsym(handle, "TfLiteXNNPackDelegateOptionsDefault");
    auto fn_TfLiteXNNPackDelegateCreate = (decltype(&TfLiteXNNPackDelegateCreate))dlsym(handle, "TfLiteXNNPackDelegateCreate");

    const char* model_path = "/data/local/tmp/indicf5_dit_int8.tflite";
    TfLiteModel* model = fn_TfLiteModelCreateFromFile(model_path);
    if (!model) {
        std::cerr << "Failed to load model from " << model_path << std::endl;
        return 1;
    }
    std::cout << "Model loaded!" << std::endl;

    // Test with XNNPACK Default vs Flags=0 vs No Delegate
    auto test_config = [&](const char* name, int flags_mode) {
        std::cout << "\n--- Testing Configuration: " << name << " ---" << std::endl;
        TfLiteInterpreterOptions* opts = fn_TfLiteInterpreterOptionsCreate();
        fn_TfLiteInterpreterOptionsSetNumThreads(opts, 4);

        TfLiteDelegate* delegate = nullptr;
        if (flags_mode >= 0) {
            delegate = fn_TfLiteXNNPackDelegateCreate(nullptr);
            if (delegate) {
                fn_TfLiteInterpreterOptionsAddDelegate(opts, delegate);
                std::cout << "  Attached XNNPACK delegate with nullptr (official defaults)" << std::endl;
            } else {
                std::cout << "  TfLiteXNNPackDelegateCreate returned NULL!" << std::endl;
            }
        }

        TfLiteInterpreter* interp = fn_TfLiteInterpreterCreate(model, opts);
        fn_TfLiteInterpreterOptionsDelete(opts);
        if (!interp) {
            std::cerr << "  Failed to create interpreter!" << std::endl;
            return;
        }

        if (fn_TfLiteInterpreterAllocateTensors(interp) != kTfLiteOk) {
            std::cerr << "  AllocateTensors FAILED!" << std::endl;
            return;
        }
        std::cout << "  AllocateTensors SUCCESS!" << std::endl;

        TfLiteTensor* in_x = fn_TfLiteInterpreterGetInputTensor(interp, 0);
        TfLiteTensor* in_cond = fn_TfLiteInterpreterGetInputTensor(interp, 1);
        TfLiteTensor* in_text = fn_TfLiteInterpreterGetInputTensor(interp, 2);
        TfLiteTensor* in_t = fn_TfLiteInterpreterGetInputTensor(interp, 3);
        const TfLiteTensor* out_v = fn_TfLiteInterpreterGetOutputTensor(interp, 0);

        // Fill exact inputs
        std::vector<float> mel(512 * 100, 0.5f);
        std::vector<float> cond(512 * 100, 0.0f);
        std::vector<int32_t> txt(128, -1);
        float t_val = 0.0f;

        std::memcpy(fn_TfLiteTensorData(in_x), mel.data(), 512 * 100 * sizeof(float));
        std::memcpy(fn_TfLiteTensorData(in_cond), cond.data(), 512 * 100 * sizeof(float));
        std::memcpy(fn_TfLiteTensorData(in_text), txt.data(), 128 * sizeof(int32_t));
        std::memcpy(fn_TfLiteTensorData(in_t), &t_val, sizeof(float));

        std::cout << "  Invoking DiT..." << std::endl;
        TfLiteStatus st = fn_TfLiteInterpreterInvoke(interp);
        if (st != kTfLiteOk) {
            std::cerr << "  Invoke FAILED (status=" << st << ")!" << std::endl;
            return;
        }

        const float* out = reinterpret_cast<const float*>(fn_TfLiteTensorData(out_v));
        float norm = 0.0f;
        int nans = 0;
        for (int i = 0; i < 512 * 100; ++i) {
            if (std::isnan(out[i])) nans++;
            else norm += out[i] * out[i];
        }
        norm = std::sqrt(norm);
        std::cout << "  Invoke Result: norm=" << norm << ", nans=" << nans << std::endl;
        std::cout << "  First 5 floats: [" << out[0] << ", " << out[1] << ", " << out[2] << ", " << out[3] << ", " << out[4] << "]" << std::endl;
    };

    test_config("XNNPACK nullptr Defaults", 0);

    return 0;
}
