#include "kiss_fftr.h"

struct kiss_fftr_state {
    kiss_fft_cfg substate;
    kiss_fft_cpx * tmpbuf;
    kiss_fft_cpx * super_twiddles;
    int nfft;
};

kiss_fftr_cfg kiss_fftr_alloc(int nfft, int inverse_fft, void * mem, size_t * lenmem) {
    int i;
    kiss_fftr_cfg st = NULL;
    size_t subsize, memneeded;

    if (nfft & 1) return NULL; // nfft must be even
    nfft >>= 1;

    kiss_fft_alloc(nfft, inverse_fft, NULL, &subsize);
    memneeded = sizeof(struct kiss_fftr_state) + subsize + sizeof(kiss_fft_cpx) * (nfft * 2);

    if (lenmem == NULL) {
        st = (kiss_fftr_cfg)KISS_FFT_MALLOC(memneeded);
    } else {
        if (*lenmem >= memneeded) st = (kiss_fftr_cfg)mem;
        *lenmem = memneeded;
    }
    if (!st) return NULL;

    st->substate = (kiss_fft_cfg)(st + 1);
    st->tmpbuf = (kiss_fft_cpx*)(((char*)st->substate) + subsize);
    st->super_twiddles = st->tmpbuf + nfft;
    kiss_fft_alloc(nfft, inverse_fft, st->substate, &subsize);

    st->nfft = nfft;

    for (i = 0; i < nfft / 2; ++i) {
        double phase = -3.1415926535897932384626433832795 * ((double)(i + 1) / nfft + 0.5);
        if (inverse_fft) phase = -phase;
        st->super_twiddles[i].r = (kiss_fft_scalar)cos(phase);
        st->super_twiddles[i].i = (kiss_fft_scalar)sin(phase);
    }
    return st;
}

void kiss_fftr(kiss_fftr_cfg st, const kiss_fft_scalar * timedata, kiss_fft_cpx * freqdata) {
    int k, ncfft;
    kiss_fft_cpx fpnk, fpk, f1k, f2k, tw, tdc;

    ncfft = st->nfft;
    kiss_fft(st->substate, (const kiss_fft_cpx*)timedata, st->tmpbuf);

    tdc.r = st->tmpbuf[0].r;
    tdc.i = st->tmpbuf[0].i;
    freqdata[0].r = tdc.r + tdc.i;
    freqdata[ncfft].r = tdc.r - tdc.i;
    freqdata[ncfft].i = freqdata[0].i = 0;

    for (k = 1; k <= ncfft / 2; ++k) {
        fpk = st->tmpbuf[k];
        fpnk.r = st->tmpbuf[ncfft - k].r;
        fpnk.i = -st->tmpbuf[ncfft - k].i;

        f1k.r = fpk.r + fpnk.r;
        f1k.i = fpk.i + fpnk.i;
        f2k.r = fpk.r - fpnk.r;
        f2k.i = fpk.i - fpnk.i;

        tw.r = f2k.r * st->super_twiddles[k - 1].r - f2k.i * st->super_twiddles[k - 1].i;
        tw.i = f2k.r * st->super_twiddles[k - 1].i + f2k.i * st->super_twiddles[k - 1].r;

        freqdata[k].r = (f1k.r + tw.r) * 0.5f;
        freqdata[k].i = (f1k.i + tw.i) * 0.5f;
        freqdata[ncfft - k].r = (f1k.r - tw.r) * 0.5f;
        freqdata[ncfft - k].i = (tw.i - f1k.i) * 0.5f;
    }
}

void kiss_fftri(kiss_fftr_cfg st, const kiss_fft_cpx * freqdata, kiss_fft_scalar * timedata) {
    int k, ncfft;
    kiss_fft_cpx * timedata_cpx = (kiss_fft_cpx*)timedata;
    ncfft = st->nfft;

    st->tmpbuf[0].r = freqdata[0].r + freqdata[ncfft].r;
    st->tmpbuf[0].i = freqdata[0].r - freqdata[ncfft].r;

    for (k = 1; k <= ncfft / 2; ++k) {
        kiss_fft_cpx fk, fnkc, fek, fok, tw;
        fk = freqdata[k];
        fnkc.r = freqdata[ncfft - k].r;
        fnkc.i = -freqdata[ncfft - k].i;

        fek.r = fk.r + fnkc.r;
        fek.i = fk.i + fnkc.i;
        fok.r = fk.r - fnkc.r;
        fok.i = fk.i - fnkc.i;

        tw.r = fok.r * st->super_twiddles[k - 1].r - fok.i * st->super_twiddles[k - 1].i;
        tw.i = fok.r * st->super_twiddles[k - 1].i + fok.i * st->super_twiddles[k - 1].r;

        st->tmpbuf[k].r = fek.r - tw.r;
        st->tmpbuf[k].i = fek.i - tw.i;
        st->tmpbuf[ncfft - k].r = fek.r + tw.r;
        st->tmpbuf[ncfft - k].i = tw.i - fek.i;
    }
    kiss_fft(st->substate, st->tmpbuf, timedata_cpx);
}
