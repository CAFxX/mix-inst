#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// Wave-11: 6-stage key-linear triplets, alt key offsets (k1=7i,k2=31i)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t ra = rotl64(x,1), rb = rotl64(x,2);
      x ^= (ra & rb) ^ rotl64(key,7) ^ rotl64(key,31); }
    { uint64_t ra = rotl64(x,7), rb = rotl64(x,19);
      x ^= (ra & rb) ^ rotl64(key,14) ^ rotl64(key,62); }
    { uint64_t ra = rotl64(x,3), rb = rotl64(x,11);
      x ^= (ra & rb) ^ rotl64(key,21) ^ rotl64(key,29); }
    { uint64_t ra = rotl64(x,17), rb = rotl64(x,31);
      x ^= (ra & rb) ^ rotl64(key,28) ^ rotl64(key,60); }
    { uint64_t ra = rotl64(x,11), rb = rotl64(x,23);
      x ^= (ra & rb) ^ rotl64(key,35) ^ rotl64(key,27); }
    { uint64_t ra = rotl64(x,19), rb = rotl64(x,41);
      x ^= (ra & rb) ^ rotl64(key,42) ^ rotl64(key,58); }
    x ^= rotl64(key, 13);
    return x;
}