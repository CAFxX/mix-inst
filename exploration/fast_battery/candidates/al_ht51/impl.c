#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// Wave-12: hetero 5-stage 2x t3 + 3x and, proxy z=3.4, est 19.05u (design-rules)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t ra = rotl64(x,51), rb = rotl64(x,49);
      x ^= (ra & rb) ^ rotl64(x,62) ^ rotl64(x,52); }
    { uint64_t ra = rotl64(x,39), rb = rotl64(x,61);
      x ^= (ra & rb) ^ rotl64(x,6); }
    { uint64_t ra = rotl64(x,7), rb = rotl64(x,17);
      x ^= (ra & rb) ^ rotl64(x,5); }
    { uint64_t ra = rotl64(x,40), rb = rotl64(x,3);
      x ^= (ra & rb) ^ rotl64(x,25); }
    { uint64_t ra = rotl64(x,33), rb = rotl64(x,29);
      x ^= (ra & rb) ^ rotl64(x,38) ^ rotl64(x,51); }
    x ^= rotl64(key, 13);
    return x;
}