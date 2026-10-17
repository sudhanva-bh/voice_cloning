#include <stdio.h>
#include <math.h>
#include "kiss_fftr.h"

int main() {
    int nfft = 8;
    kiss_fftr_cfg cfg_f = kiss_fftr_alloc(nfft, 0, NULL, NULL);
    kiss_fftr_cfg cfg_i = kiss_fftr_alloc(nfft, 1, NULL, NULL);

    float in[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    kiss_fft_cpx out[5];
    float rec[8];

    kiss_fftr(cfg_f, in, out);
    for (int i = 0; i < 5; ++i) {
        printf("out[%d] = %f + %fi\n", i, out[i].r, out[i].i);
    }

    kiss_fftri(cfg_i, out, rec);
    for (int i = 0; i < 8; ++i) {
        printf("rec[%d] = %f (expected %f)\n", i, rec[i] / nfft, in[i]);
    }
    return 0;
}
