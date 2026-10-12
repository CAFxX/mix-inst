#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 4-round nibble-OR SPN: N(x)=x^((x rol1 4b)|(x rol2 4b))
static inline uint64_t nibchi64(uint64_t x) {
    uint64_t r1 = ((x << 1) & 0xEEEEEEEEEEEEEEEEULL) | ((x >> 3) & 0x1111111111111111ULL);
    uint64_t r2 = ((x << 2) & 0xCCCCCCCCCCCCCCCCULL) | ((x >> 2) & 0x3333333333333333ULL);
    return x ^ (r1 & r2);
}
static inline uint64_t nibchi_or64(uint64_t x) {
    uint64_t r1 = ((x << 1) & 0xEEEEEEEEEEEEEEEEULL) | ((x >> 3) & 0x1111111111111111ULL);
    uint64_t r2 = ((x << 2) & 0xCCCCCCCCCCCCCCCCULL) | ((x >> 2) & 0x3333333333333333ULL);
    return x ^ (r1 | r2);
}
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t y = nibchi_or64(x);
      x = y ^ rotl64(y,13) ^ rotl64(y,29); }
    { uint64_t y = nibchi_or64(x);
      x = y ^ rotl64(y,7) ^ rotl64(y,41); }
    { uint64_t y = nibchi_or64(x);
      x = y ^ rotl64(y,17) ^ rotl64(y,5); }
    { uint64_t y = nibchi_or64(x);
      x = y ^ rotl64(y,23) ^ rotl64(y,11); }
    x ^= rotl64(key, 13);
    return x;
}