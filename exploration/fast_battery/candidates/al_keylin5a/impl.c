#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// Wave-11: 5-stage key-linear triplets (floor probe)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t ra = rotl64(x,1), rb = rotl64(x,2);
      x ^= (ra & rb) ^ rotl64(key,13) ^ rotl64(key,37); }
    { uint64_t ra = rotl64(x,7), rb = rotl64(x,19);
      x ^= (ra & rb) ^ rotl64(key,26) ^ rotl64(key,10); }
    { uint64_t ra = rotl64(x,3), rb = rotl64(x,11);
      x ^= (ra & rb) ^ rotl64(key,39) ^ rotl64(key,47); }
    { uint64_t ra = rotl64(x,17), rb = rotl64(x,31);
      x ^= (ra & rb) ^ rotl64(key,52) ^ rotl64(key,20); }
    { uint64_t ra = rotl64(x,11), rb = rotl64(x,23);
      x ^= (ra & rb) ^ rotl64(key,1) ^ rotl64(key,57); }
    x ^= rotl64(key, 13);
    return x;
}