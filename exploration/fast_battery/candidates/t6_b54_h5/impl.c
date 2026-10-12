#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-54 hetMA5p1 schedule (triage z=7.77, andpos=1);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,27)&rotl64(x,16))|((~rotl64(x,27))&rotl64(x,30))) ^ rotl64(x,31));
    x = x ^ (rotl64(x,12) & rotl64(x,54)) ^ rotl64(x,3);
    x = x ^ (((rotl64(x,62)&rotl64(x,52))|((~rotl64(x,62))&rotl64(x,53))) ^ rotl64(x,45));
    x = x ^ (((rotl64(x,10)&rotl64(x,27))|((~rotl64(x,10))&rotl64(x,16))) ^ rotl64(x,14));
    x = x ^ (((rotl64(x,20)&rotl64(x,39))|((~rotl64(x,20))&rotl64(x,36))) ^ rotl64(x,32));
    x ^= rotl64(key, 13);
    return x;
}
