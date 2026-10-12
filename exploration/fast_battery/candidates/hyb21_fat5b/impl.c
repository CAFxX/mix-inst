#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-21b proxy-guided 5-stage fat-AND schedule (triage z=2.55)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,32) & rotl64(x,43)) ^ (rotl64(x,49) & rotl64(x,9)) ^ rotl64(x,17);
    x ^= (rotl64(x,7) & rotl64(x,59)) ^ (rotl64(x,11) & rotl64(x,9)) ^ rotl64(x,30);
    x ^= (rotl64(x,21) & rotl64(x,31)) ^ (rotl64(x,50) & rotl64(x,37)) ^ rotl64(x,39);
    x ^= (rotl64(x,35) & rotl64(x,15)) ^ (rotl64(x,41) & rotl64(x,63)) ^ rotl64(x,45);
    x ^= (rotl64(x,44) & rotl64(x,23)) ^ (rotl64(x,10) & rotl64(x,46)) ^ rotl64(x,39);
    x ^= rotl64(key, 13);
    return x;
}
