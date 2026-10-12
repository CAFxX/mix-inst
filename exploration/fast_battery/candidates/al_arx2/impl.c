#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 2-addition ARX: add/xor/add/xor
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val + key;
    x ^= rotl64(x,13) ^ rotl64(x,29);
    x += rotl64(x,7);
    x ^= rotl64(x,17) ^ rotl64(x,41) ^ rotl64(x,23);
    x ^= key;
    return x;
}