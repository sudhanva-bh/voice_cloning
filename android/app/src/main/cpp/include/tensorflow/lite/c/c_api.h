#ifndef TENSORFLOW_LITE_C_C_API_H_
#define TENSORFLOW_LITE_C_C_API_H_

#include "c_api_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct TfLiteModel TfLiteModel;
typedef struct TfLiteInterpreterOptions TfLiteInterpreterOptions;
typedef struct TfLiteInterpreter TfLiteInterpreter;
typedef struct TfLiteTensor TfLiteTensor;

TFL_CAPI_EXPORT extern const char* TfLiteVersion(void);

TFL_CAPI_EXPORT extern TfLiteModel* TfLiteModelCreate(const void* model_data, size_t model_size);
TFL_CAPI_EXPORT extern TfLiteModel* TfLiteModelCreateFromFile(const char* model_path);
TFL_CAPI_EXPORT extern void TfLiteModelDelete(TfLiteModel* model);

TFL_CAPI_EXPORT extern TfLiteInterpreterOptions* TfLiteInterpreterOptionsCreate(void);
TFL_CAPI_EXPORT extern void TfLiteInterpreterOptionsDelete(TfLiteInterpreterOptions* options);
TFL_CAPI_EXPORT extern void TfLiteInterpreterOptionsSetNumThreads(TfLiteInterpreterOptions* options, int32_t num_threads);
TFL_CAPI_EXPORT extern void TfLiteInterpreterOptionsAddDelegate(TfLiteInterpreterOptions* options, TfLiteDelegate* delegate);

TFL_CAPI_EXPORT extern TfLiteInterpreter* TfLiteInterpreterCreate(const TfLiteModel* model, const TfLiteInterpreterOptions* optional_options);
TFL_CAPI_EXPORT extern void TfLiteInterpreterDelete(TfLiteInterpreter* interpreter);

TFL_CAPI_EXPORT extern int32_t TfLiteInterpreterGetInputTensorCount(const TfLiteInterpreter* interpreter);
TFL_CAPI_EXPORT extern TfLiteTensor* TfLiteInterpreterGetInputTensor(const TfLiteInterpreter* interpreter, int32_t input_index);
TFL_CAPI_EXPORT extern TfLiteStatus TfLiteInterpreterResizeInputTensor(TfLiteInterpreter* interpreter, int32_t input_index, const int* input_dims, int32_t input_dims_size);
TFL_CAPI_EXPORT extern TfLiteStatus TfLiteInterpreterAllocateTensors(TfLiteInterpreter* interpreter);
TFL_CAPI_EXPORT extern TfLiteStatus TfLiteInterpreterInvoke(TfLiteInterpreter* interpreter);

TFL_CAPI_EXPORT extern int32_t TfLiteInterpreterGetOutputTensorCount(const TfLiteInterpreter* interpreter);
TFL_CAPI_EXPORT extern const TfLiteTensor* TfLiteInterpreterGetOutputTensor(const TfLiteInterpreter* interpreter, int32_t output_index);

TFL_CAPI_EXPORT extern TfLiteType TfLiteTensorType(const TfLiteTensor* tensor);
TFL_CAPI_EXPORT extern int32_t TfLiteTensorNumDims(const TfLiteTensor* tensor);
TFL_CAPI_EXPORT extern int32_t TfLiteTensorDim(const TfLiteTensor* tensor, int32_t dim_index);
TFL_CAPI_EXPORT extern size_t TfLiteTensorByteSize(const TfLiteTensor* tensor);
TFL_CAPI_EXPORT extern void* TfLiteTensorData(const TfLiteTensor* tensor);
TFL_CAPI_EXPORT extern const char* TfLiteTensorName(const TfLiteTensor* tensor);
TFL_CAPI_EXPORT extern TfLiteStatus TfLiteTensorCopyFromBuffer(TfLiteTensor* tensor, const void* input_data, size_t input_data_size);
TFL_CAPI_EXPORT extern TfLiteStatus TfLiteTensorCopyToBuffer(const TfLiteTensor* tensor, void* output_data, size_t output_data_size);

#ifdef __cplusplus
}
#endif

#endif  // TENSORFLOW_LITE_C_C_API_H_
