/* Q1: avalanche (SAC/BIC) battery.
 * For fixed key K, N random 64-bit vals (splitmix64, fixed seed):
 *   for each input bit i: d_i = mix(v ^ 2^i, K) ^ mix(v, K)
 *   accumulate per-output-bit flip counts P[i][j].
 * Reports: sac_maxdev, sac_meandev, sac_z5 (|z|>5 cells),
 *          bic_maxcorr, bic_meancorr (Pearson corr of flip indicators
 *          F_j,F_k across trials, per input bit i, pairs j<k),
 *          avalanche_mean (mean Hamming weight of d, expect 32.0).
 * Usage: q_avalanche <impl_dir_name>   (reads ../fast_battery/candidates/<name>/impl.c via -D include at compile time)
 * Actually compiled per-candidate: gcc q_avalanche.c <cand>/impl.c -o q_avalanche_<name>
 * Output: JSON to stdout.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

uint64_t mix_hash(uint64_t val, uint64_t key);

#define NLOG 18
#define N (1u << NLOG)
#define KEY 0x123456789ABCDEF0ULL
#define SEED 0x243F6A8885A308D3ULL

static uint64_t sm64(uint64_t *s) {
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

int main(void) {
    static uint32_t flip[64][64];          /* flip[i][j]: trials where out bit j flipped for in bit i */
    static uint32_t joint[64][64][64];    /* joint[i][j][k], j<k used: both flipped */
    uint64_t s = SEED;
    unsigned long long totw = 0;          /* total hamming weight accumulator */
    unsigned long long totrials = 0;

    for (unsigned t = 0; t < N; t++) {
        uint64_t v = sm64(&s);
        uint64_t h0 = mix_hash(v, KEY);
        for (int i = 0; i < 64; i++) {
            uint64_t d = mix_hash(v ^ (1ULL << i), KEY) ^ h0;
            totw += __builtin_popcountll(d);
            totrials++;
            /* collect set-bit positions */
            int pos[64]; int c = 0;
            uint64_t dd = d;
            while (dd) { int b = __builtin_ctzll(dd); pos[c++] = b; flip[i][b]++; dd &= dd - 1; }
            for (int a = 0; a < c; a++)
                for (int b = a + 1; b < c; b++)
                    joint[i][pos[a]][pos[b]]++;
        }
    }

    double maxdev = 0, meandev = 0;
    long z5 = 0;
    double se = sqrt(0.25 / (double)N);
    for (int i = 0; i < 64; i++)
        for (int j = 0; j < 64; j++) {
            double p = (double)flip[i][j] / (double)N;
            double dev = fabs(p - 0.5);
            if (dev > maxdev) maxdev = dev;
            meandev += dev;
            if (fabs(p - 0.5) / se > 5.0) z5++;
        }
    meandev /= 4096.0;

    double maxcorr = 0, meancorr = 0;
    long long npairs = 0;
    for (int i = 0; i < 64; i++) {
        for (int j = 0; j < 64; j++) {
            double pj = (double)flip[i][j] / (double)N;
            double vj = pj * (1.0 - pj);
            if (vj <= 0) continue;
            for (int k = j + 1; k < 64; k++) {
                double pk = (double)flip[i][k] / (double)N;
                double vk = pk * (1.0 - pk);
                if (vk <= 0) continue;
                double pjk = (double)joint[i][j][k] / (double)N;
                double corr = fabs((pjk - pj * pk) / sqrt(vj * vk));
                if (corr > maxcorr) maxcorr = corr;
                meancorr += corr;
                npairs++;
            }
        }
    }
    meancorr /= (double)npairs;
    double avmean = (double)totw / (double)totrials;

    printf("{\n");
    printf("  \"key\": \"0x123456789ABCDEF0\",\n");
    printf("  \"N\": %u,\n", N);
    printf("  \"sac_maxdev\": %.6f,\n", maxdev);
    printf("  \"sac_meandev\": %.6f,\n", meandev);
    printf("  \"sac_z5\": %ld,\n", z5);
    printf("  \"bic_maxcorr\": %.6f,\n", maxcorr);
    printf("  \"bic_meancorr\": %.6f,\n", meancorr);
    printf("  \"avalanche_mean\": %.4f\n", avmean);
    printf("}\n");
    return 0;
}
