#include <stdio.h>
#include <dlfcn.h>
#include <stdlib.h>
#include <stdint.h>

int main() {
    void* handle = dlopen("/mnt/c/voice_cloning/litert-wsl-env/lib/python3.14/site-packages/ai_edge_litert/libLiteRt.so", RTLD_NOW | RTLD_GLOBAL);
    if (!handle) {
        printf("dlopen failed: %s\n", dlerror());
        return 1;
    }
    printf("libLiteRt.so loaded successfully!\n");

    void* (*p_TfLiteModelCreateFromFile)(const char*) = (void*(*)(const char*))dlsym(handle, "TfLiteModelCreateFromFile");
    void* (*p_TfLiteInterpreterOptionsCreate)(void) = (void*(*)(void))dlsym(handle, "TfLiteInterpreterOptionsCreate");
    void (*p_TfLiteInterpreterOptionsSetNumThreads)(void*, int) = (void(*)(void*, int))dlsym(handle, "TfLiteInterpreterOptionsSetNumThreads");
    void* (*p_TfLiteInterpreterCreate)(void*, void*) = (void*(*)(void*, void*))dlsym(handle, "TfLiteInterpreterCreate");
    int (*p_TfLiteInterpreterAllocateTensors)(void*) = (int(*)(void*))dlsym(handle, "TfLiteInterpreterAllocateTensors");
    void* (*p_TfLiteInterpreterGetTensor)(void*, int) = (void*(*)(void*, int))dlsym(handle, "TfLiteInterpreterGetTensor");
    void* (*p_TfLiteTensorData)(void*) = (void*(*)(void*))dlsym(handle, "TfLiteTensorData");
    size_t (*p_TfLiteTensorByteSize)(void*) = (size_t(*)(void*))dlsym(handle, "TfLiteTensorByteSize");
    const char* (*p_TfLiteTensorName)(void*) = (const char*(*)(void*))dlsym(handle, "TfLiteTensorName");
    int (*p_TfLiteInterpreterInvoke)(void*) = (int(*)(void*))dlsym(handle, "TfLiteInterpreterInvoke");

    void* model = p_TfLiteModelCreateFromFile("models/indicf5/indicf5_dit_int8.tflite");
    printf("Model: %p\n", model);
    void* options = p_TfLiteInterpreterOptionsCreate();
    p_TfLiteInterpreterOptionsSetNumThreads(options, 4);
    void* interp = p_TfLiteInterpreterCreate(model, options);
    printf("Interp: %p\n", interp);
    int alloc_res = p_TfLiteInterpreterAllocateTensors(interp);
    printf("AllocateTensors result: %d\n", alloc_res);

    void* t402 = p_TfLiteInterpreterGetTensor(interp, 402);
    printf("t402: %p, name: %s, bytes: %zu, data: %p\n", t402, p_TfLiteTensorName(t402), p_TfLiteTensorByteSize(t402), p_TfLiteTensorData(t402));

    return 0;
}
