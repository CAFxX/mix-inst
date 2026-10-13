// Track 6 batch 5: t6_maj6 — 6-stage majority cascade on rotated state.
// Bit-exact port of candidates/t6_maj6/model.py `cascade(v, k, "maj", SCHED6)`
// (emitted 2026-10-09 by mix-search-status-30m: the gen_t6_b5.py flow left
// impl.c as a stub, which killed the local S1's diffprof/gen builds at
// run_fast_battery.sh:48. NOTE: post-step is x ^= (k >> 32), as the code
// does — the model.py docstring's "post x ^= rotl(k,13)" is stale.)
#include <stdint.h>

static uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    if (!r) return x;
    return (x << r) | (x >> (64 - r));
}

static uint64_t maj3(uint64_t a, uint64_t b, uint64_t c) {
    return (a & b) | (a & c) | (b & c);
}

static const uint64_t RC64[8] = {
    0x9E3779B97F4A7C15ULL, 0x3C6EF372FE94F82AULL,
    0xDAA66D2C7DDF743FULL, 0x78DDE6E5FD29F054ULL,
    0x2545F4914F6CDD1DULL, 0x9E3779B97F4A7C15ULL ^ 0xDEADBEEFULL,
    0x3C6EF372FE94F82AULL ^ 0x12345678ULL, 0xDAA66D2C7DDF743FULL ^ 0xABCDEF01ULL
};

static const int SCHED6[6][4] = {
    { 1,  2, 13,  7},
    { 7, 19,  5, 17},
    { 3, 11, 29, 23},
    {17, 31,  7, 11},
    {11, 23, 37,  5},
    {19, 41, 23, 13}
};

uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    for (int i = 0; i < 6; i++) {
        uint64_t r0 = rotl64(x, SCHED6[i][0]);
        uint64_t r1 = rotl64(x, SCHED6[i][1]);
        uint64_t r2 = rotl64(x, SCHED6[i][2]);
        uint64_t r3 = rotl64(x, SCHED6[i][3]);
        /* x ^= maj(ra,rb,rc) ^ rd */
        x ^= maj3(r0, r1, r2) ^ r3;
        /* rk = rotl64(k, 13*(i+1)) ^ RC64[i % 8] */
        x ^= rotl64(k, 13 * (i + 1)) ^ RC64[i & 7];
    }
    /* post: x ^= (k >> 32) */
    return x ^ (k >> 32);
}
