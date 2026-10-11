/* Differential profiler for r3_xorlin_qm (peer-review remediation, stats C2).
 * For each low-weight input delta, measures the output-difference distribution
 * over N sequential inputs (the deployment distribution):
 *   dx = h(x) ^ h(x ^ delta)
 * Reports per bit: max |z| of P(dx bit = 1) vs 0.5
 *   low8: chi-square of (dx & 0xFF) histogram vs uniform (255 dof)
 *   full: number of repeated 64-bit dx values (expect ~0 under uniform)
 * Usage: ./diffprof [key_hex] [log2N]
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static const uint8_t SBOX[16] = {0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2};
static const uint64_t GOLDEN = 0x9E3779B97F4A7C15ULL;

static uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static uint64_t sbox_layer(uint64_t x) {
    uint64_t y = 0;
    for (int b = 0; b < 16; b++) y |= (uint64_t)SBOX[(x >> (4*b)) & 0xF] << (4*b);
    return y;
}
static uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    for (int i = 0; i < 4; i++) {
        uint64_t rk = rotl64(key, 13*(i+1)) ^ ((uint64_t)(i+1) * GOLDEN);
        x ^= rk;
        x = sbox_layer(x);
        x = x ^ rotl64(x, 11) ^ rotl64(x, 37);
    }
    return x ^ (rotl64(key, 13*5) ^ ((uint64_t)5 * GOLDEN));
}

/* open-addressing set for 64-bit dx repeat detection */
typedef struct { uint64_t *t; size_t mask; } HSet;
static HSet hs_new(size_t pow2) {
    HSet h; h.mask = (1UL<<pow2)-1;
    h.t = calloc(1UL<<pow2, sizeof(uint64_t));
    for (size_t i=0;i<=h.mask;i++) h.t[i]=0xFFFFFFFFFFFFFFFFULL; /* empty marker impossible? dx can be all-ones... use separate used bitmap */
    return h;
}

int main(int argc, char **argv) {
    uint64_t key = argc > 1 ? strtoull(argv[1], NULL, 16) : 0x123456789ABCDEF0ULL;
    int logN = argc > 2 ? atoi(argv[2]) : 22;
    uint64_t N = 1ULL << logN;

    /* cross-check marker vs numpy model (A2/C5): h(0), h(1) printed for external diff */
    printf("# model check: h(0)=%016llx h(1)=%016llx h(0xffffffffffffffff)=%016llx\n",
        (unsigned long long)mix_hash(0,key),
        (unsigned long long)mix_hash(1,key),
        (unsigned long long)mix_hash(0xFFFFFFFFFFFFFFFFULL,key));

    /* deltas: 64x weight-1, plus a few weight-2 */
    uint64_t deltas[72]; int nd=0;
    for (int k=0;k<64;k++) deltas[nd++] = 1ULL<<k;
    uint64_t w2[] = {3ULL, 5ULL, 9ULL, 0x11ULL, 0x8000000000000001ULL, 0x100000001ULL, 0xF0F0F0F0F0F0F0F0ULL, 0xFFFFFFFFFFFFFFFFULL};
    for (int i=0;i<8;i++) deltas[nd++] = w2[i];

    uint64_t *bitcnt = calloc(64, sizeof(uint64_t));
    uint64_t *h8 = calloc(256, sizeof(uint64_t));
    /* hash set sized 2*2^logN entries */
    size_t HP = (size_t)logN + 2;
    uint64_t *ht = malloc((1UL<<HP)*sizeof(uint64_t));
    uint8_t *used = calloc(1UL<<HP, 1);

    printf("# key=%016llx pairs=2^%d (deduped)\n", (unsigned long long)key, logN-1);
    printf("# %-20s %8s %10s %12s\n", "delta", "max|z|", "low8_chi2", "full_repeats");
    for (int d=0; d<nd; d++) {
        uint64_t dl = deltas[d];
        memset(bitcnt, 0, 64*sizeof(uint64_t));
        memset(h8, 0, 256*sizeof(uint64_t));
        memset(used, 0, 1UL<<HP);
        uint64_t repeats = 0, npairs = 0;
        for (uint64_t x=0; x<N; x++) {
            if (x > (x^dl)) continue; /* canonical unordered pair: dedupe */
            npairs++;
            uint64_t dx = mix_hash(x,key) ^ mix_hash(x^dl,key);
            for (int b=0;b<64;b++) bitcnt[b] += (dx>>b)&1;
            h8[dx & 0xFF]++;
            /* insert into set */
            size_t h = (size_t)(dx * 0x9E3779B97F4A7C15ULL) >> (64-HP);
            while (used[h]) {
                if (ht[h]==dx) { repeats++; break; }
                h = (h+1) & ((1UL<<HP)-1);
            }
            if (!used[h]) { used[h]=1; ht[h]=dx; }
        }
        double maxz = 0;
        for (int b=0;b<64;b++) {
            double p = (double)bitcnt[b]/(double)npairs;
            double z = (p-0.5)/sqrt(0.25/(double)npairs);
            if (fabs(z)>maxz) maxz=fabs(z);
        }
        double exp8 = (double)npairs/256.0, chi2 = 0;
        for (int i=0;i<256;i++){ double df=h8[i]-exp8; chi2 += df*df/exp8; }
        printf("  0x%016llx %8.1f %10.1f %12llu\n",
            (unsigned long long)dl, maxz, chi2, (unsigned long long)repeats);
        fflush(stdout);
    }
    return 0;
}
