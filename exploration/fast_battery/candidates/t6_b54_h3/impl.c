#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-54 hetMA5p1 schedule (triage z=5.52, andpos=1);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,47)&rotl64(x,28))|((~rotl64(x,47))&rotl64(x,14))) ^ rotl64(x,18));
    x = x ^ (rotl64(x,7) & rotl64(x,10)) ^ rotl64(x,1);
    x = x ^ (((rotl64(x,49)&rotl64(x,54))|((~rotl64(x,49))&rotl64(x,33))) ^ rotl64(x,38));
    x = x ^ (((rotl64(x,35)&rotl64(x,59))|((~rotl64(x,35))&rotl64(x,16))) ^ rotl64(x,9));
    x = x ^ (((rotl64(x,63)&rotl64(x,32))|((~rotl64(x,63))&rotl64(x,28))) ^ rotl64(x,40));
    x ^= rotl64(key, 13);
    return x;
}
