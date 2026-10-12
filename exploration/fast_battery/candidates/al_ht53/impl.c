#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// Wave-12: hetero 5-stage 2x t3 + 3x and, proxy z=4.8, est 19.05u (design-rules)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    { uint64_t ra = rotl64(x,17), rb = rotl64(x,19);
      x ^= (ra & rb) ^ rotl64(x,30) ^ rotl64(x,28); }
    { uint64_t ra = rotl64(x,14), rb = rotl64(x,60);
      x ^= (ra & rb) ^ rotl64(x,29); }
    { uint64_t ra = rotl64(x,26), rb = rotl64(x,10);
      x ^= (ra & rb) ^ rotl64(x,40); }
    { uint64_t ra = rotl64(x,59), rb = rotl64(x,2);
      x ^= (ra & rb) ^ rotl64(x,41); }
    { uint64_t ra = rotl64(x,24), rb = rotl64(x,6);
      x ^= (ra & rb) ^ rotl64(x,15) ^ rotl64(x,13); }
    x ^= rotl64(key, 13);
    return x;
}