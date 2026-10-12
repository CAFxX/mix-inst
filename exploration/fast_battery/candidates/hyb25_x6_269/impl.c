#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb25_x6_269: batch-25 X6 6-stage XOR-fed chain (triage z=2.69)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint64_t u;
    u = rotl64(x,38) & rotl64(x,12);
    x ^= u ^ rotl64(x,22);
    u = rotl64(x,15) & (rotl64(u,4) ^ rotl64(x,56));
    x ^= u ^ rotl64(x,33);
    u = rotl64(x,41) & (rotl64(u,54) ^ rotl64(x,47));
    x ^= u ^ rotl64(x,21);
    u = rotl64(x,62) & (rotl64(u,39) ^ rotl64(x,56));
    x ^= u ^ rotl64(x,32);
    u = rotl64(x,1) & (rotl64(u,26) ^ rotl64(x,9));
    x ^= u ^ rotl64(x,38);
    u = rotl64(x,23) & (rotl64(u,43) ^ rotl64(x,36));
    x ^= u ^ rotl64(x,3);
    x ^= rotl64(key, 13);
    return x;
}
