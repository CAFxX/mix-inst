#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// Wave-11: 5xAND+1xLIN, linear stage at idx 0 (resonance-break)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t ra = rotl64(x,21), rb = rotl64(x,39);
      x ^= ra ^ rb ^ rotl64(x,57); }
    { uint64_t ra = rotl64(x,7), rb = rotl64(x,19);
      x ^= (ra & rb) ^ rotl64(x,5); }
    { uint64_t ra = rotl64(x,3), rb = rotl64(x,11);
      x ^= (ra & rb) ^ rotl64(x,29); }
    { uint64_t ra = rotl64(x,17), rb = rotl64(x,31);
      x ^= (ra & rb) ^ rotl64(x,7); }
    { uint64_t ra = rotl64(x,11), rb = rotl64(x,23);
      x ^= (ra & rb) ^ rotl64(x,37); }
    { uint64_t ra = rotl64(x,19), rb = rotl64(x,41);
      x ^= (ra & rb) ^ rotl64(x,23); }
    x ^= rotl64(key, 13);
    return x;
}