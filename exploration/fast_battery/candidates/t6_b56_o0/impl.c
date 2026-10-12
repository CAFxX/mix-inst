#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-56 hetMOA5 schedule (fisher triage z=2.71 n_reject=0, andpos=1);
// the linear mask (ra / rd) is load-bearing (zero-corner).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,30)&rotl64(x,27))|((~rotl64(x,30))&rotl64(x,19))) ^ rotl64(x,56));
    x = x ^ (((rotl64(x,18)|rotl64(x,42))&rotl64(x,6)) ^ rotl64(x,16));
    x = x ^ (((rotl64(x,3)&rotl64(x,54))|((~rotl64(x,3))&rotl64(x,40))) ^ rotl64(x,6));
    x = x ^ (((rotl64(x,61)&rotl64(x,33))|((~rotl64(x,61))&rotl64(x,16))) ^ rotl64(x,54));
    x = x ^ (((rotl64(x,41)&rotl64(x,18))|((~rotl64(x,41))&rotl64(x,2))) ^ rotl64(x,3));
    x ^= rotl64(key, 13);
    return x;
}
