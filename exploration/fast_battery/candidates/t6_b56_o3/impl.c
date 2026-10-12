#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-56 hetMOA5 schedule (fisher triage z=3.56 n_reject=0, andpos=1);
// the linear mask (ra / rd) is load-bearing (zero-corner).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,62)&rotl64(x,50))|((~rotl64(x,62))&rotl64(x,19))) ^ rotl64(x,6));
    x = x ^ (((rotl64(x,53)|rotl64(x,61))&rotl64(x,9)) ^ rotl64(x,28));
    x = x ^ (((rotl64(x,43)&rotl64(x,52))|((~rotl64(x,43))&rotl64(x,11))) ^ rotl64(x,12));
    x = x ^ (((rotl64(x,7)&rotl64(x,57))|((~rotl64(x,7))&rotl64(x,30))) ^ rotl64(x,10));
    x = x ^ (((rotl64(x,46)&rotl64(x,55))|((~rotl64(x,46))&rotl64(x,49))) ^ rotl64(x,36));
    x ^= rotl64(key, 13);
    return x;
}
