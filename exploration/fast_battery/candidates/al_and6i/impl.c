#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// 6-stage AND-rotation cascade, avalanche-aware schedule I
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t r[3] = {rotl64(x,32), rotl64(x,3), rotl64(x,41)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,30), rotl64(x,55), rotl64(x,23)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,35), rotl64(x,6), rotl64(x,45)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,54), rotl64(x,33), rotl64(x,7)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,18), rotl64(x,5), rotl64(x,48)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    { uint64_t r[3] = {rotl64(x,10), rotl64(x,17), rotl64(x,28)};
      x ^= (r[0] & r[1]) ^ r[2]; }
    x ^= rotl64(key, 13);
    return x;
}