#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-55 hetMA5p1f schedule (fisher triage z=2.90 n_reject=0, andpos=1);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,43)&rotl64(x,22))|((~rotl64(x,43))&rotl64(x,44))) ^ rotl64(x,45));
    x = x ^ (rotl64(x,49) & rotl64(x,47)) ^ rotl64(x,40);
    x = x ^ (((rotl64(x,23)&rotl64(x,21))|((~rotl64(x,23))&rotl64(x,16))) ^ rotl64(x,20));
    x = x ^ (((rotl64(x,4)&rotl64(x,5))|((~rotl64(x,4))&rotl64(x,12))) ^ rotl64(x,38));
    x = x ^ (((rotl64(x,9)&rotl64(x,51))|((~rotl64(x,9))&rotl64(x,53))) ^ rotl64(x,17));
    x ^= rotl64(key, 13);
    return x;
}
