#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-54 hetMA5p1 schedule (triage z=4.28, andpos=1);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,37)&rotl64(x,19))|((~rotl64(x,37))&rotl64(x,10))) ^ rotl64(x,57));
    x = x ^ (rotl64(x,23) & rotl64(x,42)) ^ rotl64(x,12);
    x = x ^ (((rotl64(x,9)&rotl64(x,15))|((~rotl64(x,9))&rotl64(x,24))) ^ rotl64(x,17));
    x = x ^ (((rotl64(x,16)&rotl64(x,52))|((~rotl64(x,16))&rotl64(x,24))) ^ rotl64(x,63));
    x = x ^ (((rotl64(x,43)&rotl64(x,13))|((~rotl64(x,43))&rotl64(x,12))) ^ rotl64(x,35));
    x ^= rotl64(key, 13);
    return x;
}
