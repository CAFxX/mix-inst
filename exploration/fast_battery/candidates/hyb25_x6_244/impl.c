#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb25_x6_244: batch-25 X6 6-stage XOR-fed chain (triage z=2.44)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t u;
    u = rotl64(x,2) & rotl64(x,10);
    x ^= u ^ rotl64(x,48);
    u = rotl64(x,42) & (rotl64(u,10) ^ rotl64(x,38));
    x ^= u ^ rotl64(x,13);
    u = rotl64(x,14) & (rotl64(u,35) ^ rotl64(x,11));
    x ^= u ^ rotl64(x,25);
    u = rotl64(x,33) & (rotl64(u,25) ^ rotl64(x,1));
    x ^= u ^ rotl64(x,26);
    u = rotl64(x,41) & (rotl64(u,57) ^ rotl64(x,16));
    x ^= u ^ rotl64(x,23);
    u = rotl64(x,31) & (rotl64(u,58) ^ rotl64(x,46));
    x ^= u ^ rotl64(x,21);
    x ^= rotl64(key, 13);
    return x;
}
