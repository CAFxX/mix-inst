/* S2 differential early-kill profiler (fast staged battery).
 * Compiled per-candidate together with candidates/<name>/impl.c which must
 * define: uint64_t mix_hash(uint64_t val, uint64_t key).
 *
 * Modes:
 *   ./diffprof --hash <vecfile>     lines "v k" -> "v k h(v,k)"   (xcheck vs Python)
 *   ./diffprof --dx   <vecfile>     lines "x dl key" -> "x dl key dx"
 *   ./diffprof <key_hex> [log2N] [kill_repeats]
 *        differential sweep over 64 weight-1 deltas + structured deltas +
 *        single-nibble deltas (DDT-driven: all 15 nonzero nibble values at
 *        4 representative positions, covering every S-box input difference),
 *        N = 2^log2N sequential inputs (deduped unordered pairs).
 *        Prints per-delta: max|z| (per-bit flip bias), low-8-bit chi2,
 *        full-64-bit output-difference repeats.
 *        EARLY KILL: stops at the first delta whose repeats exceed
 *        kill_repeats and prints "KILL repeats=...".
 *
 * Kill threshold (2026-10-02, peer review MAJOR-7): under the null (random
 * 64-bit outputs), E[repeats] per delta = 2^logN * 2^-64 ≈ 2^-42 at logN=22.
 * ANY repeat is ~2^42 above null, so the threshold is principled at a small
 * value, not the old arbitrary 1000. Default kill_repeats=10 (≈2^39 above
 * null — still definitive, with headroom for hash-table pathology).
 *
 *
 * Delta order: a few historically-suspicious structured deltas first
 * (0x400, 0x4000000 caught h_xorspn3), then all 64 weight-1 deltas, then the
 * remaining structured deltas. This makes known-bad constructions die fast.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

uint64_t mix_hash(uint64_t val, uint64_t key);

static int mode_hash_vecs(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { perror("fopen"); return 1; }
    char line[256];
    while (fgets(line, sizeof line, f)) {
        unsigned long long v, k;
        if (sscanf(line, "%llx %llx", &v, &k) != 2) continue;
        printf("%016llx %016llx %016llx\n", v, k,
               (unsigned long long)mix_hash(v, k));
    }
    fclose(f);
    return 0;
}

static int mode_dx_vecs(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { perror("fopen"); return 1; }
    char line[256];
    while (fgets(line, sizeof line, f)) {
        unsigned long long x, dl, k;
        if (sscanf(line, "%llx %llx %llx", &x, &dl, &k) != 3) continue;
        uint64_t dx = mix_hash(x, k) ^ mix_hash(x ^ dl, k);
        printf("%016llx %016llx %016llx %016llx\n", x, dl, k,
               (unsigned long long)dx);
    }
    fclose(f);
    return 0;
}

int main(int argc, char **argv) {
    if (argc > 1 && strcmp(argv[1], "--hash") == 0)
        return mode_hash_vecs(argv[2]);
    if (argc > 1 && strcmp(argv[1], "--dx") == 0)
        return mode_dx_vecs(argv[2]);

    uint64_t key = argc > 1 ? strtoull(argv[1], NULL, 16) : 0x123456789ABCDEF0ULL;
    int logN = argc > 2 ? atoi(argv[2]) : 22;
    unsigned long long kill_repeats =
        argc > 3 ? strtoull(argv[3], NULL, 10) : 10ULL;
    uint64_t N = 1ULL << logN;

    /* delta order: suspicious structured first, then all weight-1, then rest */
    uint64_t deltas[160]; int nd = 0;
    deltas[nd++] = 0x400ULL;
    deltas[nd++] = 0x4000000ULL;
    for (int k = 0; k < 64; k++) deltas[nd++] = 1ULL << k;
    uint64_t w2[] = {3ULL, 5ULL, 9ULL, 0x11ULL, 0x8000000000000001ULL,
                     0x100000001ULL, 0xF0F0F0F0F0F0F0F0ULL, 0xFFFFFFFFFFFFFFFFULL};
    for (int i = 0; i < 8; i++) {
        uint64_t d = w2[i];
        int seen = 0;
        for (int j = 0; j < nd; j++) if (deltas[j] == d) { seen = 1; break; }
        if (!seen) deltas[nd++] = d;
    }
    /* DDT-driven single-nibble deltas (2026-10-02, peer review MAJOR-8):
     * every nonzero 4-bit value at 4 representative nibble positions
     * (0, 7, 8, 15 — low/high nibble of each 32-bit half). The S-box
     * differential is position-independent, so this covers the full DDT
     * input space including the worst diffs (0x6,0xA,0xC,0xD,0xF at DP 2^-2
     * for S1). S-box-agnostic: works for any 4-bit S-box candidate. */
    for (int v = 1; v < 16; v++) {
        for (int pos = 0; pos < 4; pos++) {
            int nib = (pos == 0) ? 0 : (pos == 1) ? 7 : (pos == 2) ? 8 : 15;
            uint64_t d = (uint64_t)v << (4 * nib);
            int seen = 0;
            for (int j = 0; j < nd; j++) if (deltas[j] == d) { seen = 1; break; }
            if (!seen) deltas[nd++] = d;
        }
    }

    uint64_t *bitcnt = calloc(64, sizeof(uint64_t));
    uint64_t *h8 = calloc(256, sizeof(uint64_t));
    size_t HP = (size_t)logN + 2;
    uint64_t *ht = malloc((1UL<<HP)*sizeof(uint64_t));
    uint8_t *used = calloc(1UL<<HP, 1);

    printf("# key=%016llx N=2^%d kill_repeats=%llu\n",
           (unsigned long long)key, logN, kill_repeats);
    /* Null expectation: 2^logN unordered pairs, P(collision)=2^-64 each. */
    printf("# null E[repeats/delta] = 2^%d * 2^-64 = 2^%d\n", logN, logN - 64);
    printf("# %-20s %8s %10s %12s\n", "delta", "max|z|", "low8_chi2", "full_repeats");
    unsigned long long gmax_rep = 0;
    double gmax_z = 0;
    for (int d = 0; d < nd; d++) {
        uint64_t dl = deltas[d];
        memset(bitcnt, 0, 64*sizeof(uint64_t));
        memset(h8, 0, 256*sizeof(uint64_t));
        memset(used, 0, 1UL<<HP);
        uint64_t repeats = 0, npairs = 0;
        for (uint64_t x = 0; x < N; x++) {
            if (x > (x^dl)) continue; /* canonical unordered pair: dedupe */
            npairs++;
            uint64_t dx = mix_hash(x,key) ^ mix_hash(x^dl,key);
            for (int b = 0; b < 64; b++) bitcnt[b] += (dx>>b)&1;
            h8[dx & 0xFF]++;
            size_t h = (size_t)(dx * 0x9E3779B97F4A7C15ULL) >> (64-HP);
            while (used[h]) {
                if (ht[h] == dx) { repeats++; break; }
                h = (h+1) & ((1UL<<HP)-1);
            }
            if (!used[h]) { used[h] = 1; ht[h] = dx; }
        }
        double maxz = 0;
        for (int b = 0; b < 64; b++) {
            double p = (double)bitcnt[b]/(double)npairs;
            double z = (p-0.5)/sqrt(0.25/(double)npairs);
            if (fabs(z) > maxz) maxz = fabs(z);
        }
        double exp8 = (double)npairs/256.0, chi2 = 0;
        for (int i = 0; i < 256; i++) { double df = h8[i]-exp8; chi2 += df*df/exp8; }
        printf("  0x%016llx %8.1f %10.1f %12llu\n",
            (unsigned long long)dl, maxz, chi2, (unsigned long long)repeats);
        fflush(stdout);
        if (repeats > gmax_rep) gmax_rep = repeats;
        if (maxz > gmax_z) gmax_z = maxz;
        if (repeats > kill_repeats) {
            printf("KILL delta=0x%016llx repeats=%llu > kill_repeats=%llu\n",
                (unsigned long long)dl, (unsigned long long)repeats, kill_repeats);
            return 2;
        }
    }
    printf("PASS max_repeats=%llu max|z|=%.1f (all %d deltas)\n",
           gmax_rep, gmax_z, nd);
    return 0;
}
