#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// QLOW: probe-mined minimal-AND bijective quadratic 4-bit
// S-box (batch-50); ANF derived from the LUT by Moebius,
// bit-exact on all 16 inputs.
static inline uint64_t qlow(uint64_t x) {
    const uint64_t M = 0x1111111111111111ULL;
    uint64_t X0 = x & M;
    uint64_t X1 = (x >> 1) & M;
    uint64_t X2 = (x >> 2) & M;
    uint64_t X3 = (x >> 3) & M;
    uint64_t A01 = X0 & X1;
    uint64_t A02 = X0 & X2;
    uint64_t A03 = X0 & X3;
    uint64_t Y0 = X0;
    uint64_t Y1 = M ^ X0 ^ A01 ^ X2 ^ X3 ^ A03;
    uint64_t Y2 = X0 ^ X1 ^ A01 ^ A02 ^ A03;
    uint64_t Y3 = M ^ X1 ^ A01 ^ X3;
    return Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3);
}
// batch-50 qlowS4 schedule (triage z=5.57)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t y;
    y = qlow(x); x = y ^ rotl64(y,55) ^ rotl64(y,9);
    y = qlow(x); x = y ^ rotl64(y,59) ^ rotl64(y,42);
    y = qlow(x); x = y ^ rotl64(y,45) ^ rotl64(y,35);
    y = qlow(x); x = y ^ rotl64(y,10) ^ rotl64(y,37);
    x ^= rotl64(key, 13);
    return x;
}
