#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// Q4: mined bijective quadratic 4-bit S-box (batch-49),
// ANF bit-exact vs LUT [3,4,15,5,0,6,1,10,14,13,2,12,9,11,8,7].
static inline uint64_t q4(uint64_t x) {
    const uint64_t M = 0x1111111111111111ULL;
    uint64_t X0 = x & M, X1 = (x >> 1) & M,
               X2 = (x >> 2) & M, X3 = (x >> 3) & M;
    uint64_t A01 = X0 & X1, A02 = X0 & X2, A12 = X1 & X2,
               A03 = X0 & X3, A23 = X2 & X3;
    uint64_t Y0 = M ^ X0 ^ X2 ^ X3 ^ A01 ^ A02 ^ A12;
    uint64_t Y1 = M ^ X0 ^ X2;
    uint64_t Y2 = X0 ^ X1 ^ X3 ^ A01 ^ A12 ^ A03 ^ A23;
    uint64_t Y3 = X1 ^ X3 ^ A01 ^ A12;
    return Y0 | (Y1 << 1) | (Y2 << 2) | (Y3 << 3);
}
// batch-49 q4bS4 schedule (triage z=2.61)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t y;
    y = q4(x); x = y ^ rotl64(y,21) ^ rotl64(y,37);
    y = q4(x); x = y ^ rotl64(y,55) ^ rotl64(y,60);
    y = q4(x); x = y ^ rotl64(y,12) ^ rotl64(y,19);
    y = q4(x); x = y ^ rotl64(y,41) ^ rotl64(y,15);
    x ^= rotl64(key, 13);
    return x;
}
