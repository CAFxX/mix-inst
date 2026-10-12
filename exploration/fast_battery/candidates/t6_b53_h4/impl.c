#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-53 hetMA5 schedule (triage z=9.89, andpos=2);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,25)&rotl64(x,27))|((~rotl64(x,25))&rotl64(x,28))) ^ rotl64(x,34));
    x = x ^ (((rotl64(x,62)&rotl64(x,2))|((~rotl64(x,62))&rotl64(x,28))) ^ rotl64(x,51));
    x = x ^ (rotl64(x,9) & rotl64(x,51)) ^ rotl64(x,54);
    x = x ^ (((rotl64(x,60)&rotl64(x,19))|((~rotl64(x,60))&rotl64(x,20))) ^ rotl64(x,37));
    x = x ^ (((rotl64(x,51)&rotl64(x,10))|((~rotl64(x,51))&rotl64(x,27))) ^ rotl64(x,52));
    x ^= rotl64(key, 13);
    return x;
}
