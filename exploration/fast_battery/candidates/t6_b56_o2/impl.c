#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-56 hetMOA5 schedule (fisher triage z=3.06 n_reject=0, andpos=1);
// the linear mask (ra / rd) is load-bearing (zero-corner).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,29)&rotl64(x,10))|((~rotl64(x,29))&rotl64(x,46))) ^ rotl64(x,63));
    x = x ^ (((rotl64(x,30)|rotl64(x,19))&rotl64(x,7)) ^ rotl64(x,44));
    x = x ^ (((rotl64(x,32)&rotl64(x,48))|((~rotl64(x,32))&rotl64(x,16))) ^ rotl64(x,55));
    x = x ^ (((rotl64(x,56)&rotl64(x,12))|((~rotl64(x,56))&rotl64(x,53))) ^ rotl64(x,10));
    x = x ^ (((rotl64(x,10)&rotl64(x,21))|((~rotl64(x,10))&rotl64(x,29))) ^ rotl64(x,27));
    x ^= rotl64(key, 13);
    return x;
}
