#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// Wave-12: hetero 5-stage 2x t3 + 3x and, proxy z=3.9, est 19.05u (design-rules)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t ra = rotl64(x,27), rb = rotl64(x,30);
      x ^= (ra & rb) ^ rotl64(x,61) ^ rotl64(x,15); }
    { uint64_t ra = rotl64(x,6), rb = rotl64(x,11);
      x ^= (ra & rb) ^ rotl64(x,10); }
    { uint64_t ra = rotl64(x,8), rb = rotl64(x,28);
      x ^= (ra & rb) ^ rotl64(x,52); }
    { uint64_t ra = rotl64(x,31), rb = rotl64(x,44);
      x ^= (ra & rb) ^ rotl64(x,2); }
    { uint64_t ra = rotl64(x,24), rb = rotl64(x,13);
      x ^= (ra & rb) ^ rotl64(x,25) ^ rotl64(x,46); }
    x ^= rotl64(key, 13);
    return x;
}