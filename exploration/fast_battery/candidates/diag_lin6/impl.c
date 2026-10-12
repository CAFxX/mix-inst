#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// diagnostic: 6-stage pure linear
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t ra = rotl64(x,9), rb = rotl64(x,27);
      x ^= ra ^ rb ^ rotl64(x,45); }
    { uint64_t ra = rotl64(x,15), rb = rotl64(x,33);
      x ^= ra ^ rb ^ rotl64(x,51); }
    { uint64_t ra = rotl64(x,21), rb = rotl64(x,39);
      x ^= ra ^ rb ^ rotl64(x,57); }
    { uint64_t ra = rotl64(x,27), rb = rotl64(x,45);
      x ^= ra ^ rb ^ rotl64(x,9); }
    { uint64_t ra = rotl64(x,33), rb = rotl64(x,51);
      x ^= ra ^ rb ^ rotl64(x,15); }
    { uint64_t ra = rotl64(x,39), rb = rotl64(x,57);
      x ^= ra ^ rb ^ rotl64(x,21); }
    x ^= rotl64(key, 13);
    return x;
}