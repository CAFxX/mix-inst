#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31;
    return r ? (x << r) | (x >> (32 - r)) : x;
}
// Wave-10: 5-stage dual-AND, fresh schedule (floor attack, independent)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t r[5] = {rotl64(x,2), rotl64(x,9), rotl64(x,23), rotl64(x,41), rotl64(x,13)};
      x ^= (r[0] & r[1]) ^ (r[2] & r[3]) ^ r[4]; }
    { uint64_t r[5] = {rotl64(x,5), rotl64(x,17), rotl64(x,31), rotl64(x,53), rotl64(x,7)};
      x ^= (r[0] & r[1]) ^ (r[2] & r[3]) ^ r[4]; }
    { uint64_t r[5] = {rotl64(x,11), rotl64(x,29), rotl64(x,3), rotl64(x,19), rotl64(x,43)};
      x ^= (r[0] & r[1]) ^ (r[2] & r[3]) ^ r[4]; }
    { uint64_t r[5] = {rotl64(x,13), rotl64(x,37), rotl64(x,7), rotl64(x,25), rotl64(x,5)};
      x ^= (r[0] & r[1]) ^ (r[2] & r[3]) ^ r[4]; }
    { uint64_t r[5] = {rotl64(x,19), rotl64(x,47), rotl64(x,11), rotl64(x,33), rotl64(x,17)};
      x ^= (r[0] & r[1]) ^ (r[2] & r[3]) ^ r[4]; }
    x ^= rotl64(key, 13);
    return x;
}