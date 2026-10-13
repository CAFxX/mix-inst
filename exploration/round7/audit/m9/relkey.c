/* M9 item 3: related-key differential structure.
 * For key pair (k, k^delta), over N random vals compute
 *   d = mix(v,k) ^ mix(v,k^delta)
 * report: zero-d count, full-64 repeats of d, max per-bit bias |z|. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <math.h>
uint64_t mix_hash(uint64_t val, uint64_t key);
static int cmp64(const void *a, const void *b) {
    uint64_t x=*(const uint64_t*)a, y=*(const uint64_t*)b;
    return (x>y)-(x<y);
}
int main(int argc, char **argv) {
    uint64_t k = strtoull(argv[1], 0, 16);
    uint64_t delta = strtoull(argv[2], 0, 16);
    const size_t N = 1u << 20;
    uint64_t *d = malloc(N * sizeof *d);
    uint64_t k2 = k ^ delta, s = 0xabcdef123456789ULL;
    long long zd = 0;
    long long bitcnt[64] = {0};
    for (size_t i = 0; i < N; i++) {
        s = s * 6364136223846793005ULL + 1442695040888963407ULL;
        uint64_t dd = mix_hash(s, k) ^ mix_hash(s, k2);
        d[i] = dd;
        if (dd == 0) zd++;
        for (int b = 0; b < 64; b++) bitcnt[b] += (dd >> b) & 1;
    }
    qsort(d, N, sizeof *d, cmp64);
    long long rep = 0, run = 1;
    for (size_t i = 1; i < N; i++) {
        if (d[i] == d[i-1]) run++;
        else { if (run > 1) rep += run; run = 1; }
    }
    if (run > 1) rep += run;
    double mz = 0;
    for (int b = 0; b < 64; b++) {
        double z = (bitcnt[b] - N / 2.0) / sqrt(N / 4.0);
        if (fabs(z) > mz) mz = fabs(z);
    }
    printf("k=%016llx delta=%016llx N=2^20 zero_d=%lld repeat_vals=%lld max|z|=%.2f\n",
           (unsigned long long)k, (unsigned long long)delta, zd, rep, mz);
    free(d);
    return 0;
}
