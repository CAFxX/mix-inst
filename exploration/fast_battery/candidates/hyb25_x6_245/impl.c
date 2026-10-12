#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb25_x6_245: batch-25 X6 6-stage XOR-fed chain (triage z=2.45)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t u;
    u = rotl64(x,15) & rotl64(x,16);
    x ^= u ^ rotl64(x,59);
    u = rotl64(x,57) & (rotl64(u,55) ^ rotl64(x,1));
    x ^= u ^ rotl64(x,38);
    u = rotl64(x,11) & (rotl64(u,52) ^ rotl64(x,26));
    x ^= u ^ rotl64(x,57);
    u = rotl64(x,50) & (rotl64(u,12) ^ rotl64(x,18));
    x ^= u ^ rotl64(x,29);
    u = rotl64(x,16) & (rotl64(u,7) ^ rotl64(x,44));
    x ^= u ^ rotl64(x,52);
    u = rotl64(x,19) & (rotl64(u,14) ^ rotl64(x,6));
    x ^= u ^ rotl64(x,8);
    x ^= rotl64(key, 13);
    return x;
}
