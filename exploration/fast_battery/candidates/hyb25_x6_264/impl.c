#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb25_x6_264: batch-25 X6 6-stage XOR-fed chain (triage z=2.64)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t u;
    u = rotl64(x,41) & rotl64(x,59);
    x ^= u ^ rotl64(x,23);
    u = rotl64(x,58) & (rotl64(u,19) ^ rotl64(x,50));
    x ^= u ^ rotl64(x,36);
    u = rotl64(x,33) & (rotl64(u,6) ^ rotl64(x,54));
    x ^= u ^ rotl64(x,24);
    u = rotl64(x,20) & (rotl64(u,35) ^ rotl64(x,17));
    x ^= u ^ rotl64(x,27);
    u = rotl64(x,11) & (rotl64(u,46) ^ rotl64(x,42));
    x ^= u ^ rotl64(x,48);
    u = rotl64(x,19) & (rotl64(u,21) ^ rotl64(x,28));
    x ^= u ^ rotl64(x,52);
    x ^= rotl64(key, 13);
    return x;
}
