#ifndef TENSORFLOW_LITE_DELEGATES_XNNPACK_XNNPACK_DELEGATE_H_
#define TENSORFLOW_LITE_DELEGATES_XNNPACK_XNNPACK_DELEGATE_H_

#include "tensorflow/lite/c/c_api_types.h"

#ifdef __cplusplus
extern "C" {
#endif

struct TfLiteXNNPackDelegateWeightsCache;

typedef struct {
  int32_t num_threads;
  uint32_t flags;
  struct TfLiteXNNPackDelegateWeightsCache* weights_cache;
  bool handle_variable_ops;
  bool experimental_adaptive_avx_optimization;
} TfLiteXNNPackDelegateOptions;

TFL_CAPI_EXPORT extern TfLiteXNNPackDelegateOptions TfLiteXNNPackDelegateOptionsDefault(void);
TFL_CAPI_EXPORT extern TfLiteDelegate* TfLiteXNNPackDelegateCreate(const TfLiteXNNPackDelegateOptions* options);
TFL_CAPI_EXPORT extern void TfLiteXNNPackDelegateDelete(TfLiteDelegate* delegate);

#ifdef __cplusplus
}
#endif

#endif  // TENSORFLOW_LITE_DELEGATES_XNNPACK_XNNPACK_DELEGATE_H_
