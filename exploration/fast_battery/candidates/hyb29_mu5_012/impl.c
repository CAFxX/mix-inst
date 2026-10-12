#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-29 MU5-324local schedule (fisher triage z=3.09 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,62)&rotl64(x,24))|((~rotl64(x,62))&rotl64(x,55))) ^ rotl64(x,2));
    x = x ^ (((rotl64(x,48)&rotl64(x,58))|((~rotl64(x,48))&rotl64(x,23))) ^ rotl64(x,30));
    x = x ^ (((rotl64(x,44)&rotl64(x,45))|((~rotl64(x,44))&rotl64(x,7))) ^ rotl64(x,40));
    x = x ^ (((rotl64(x,49)&rotl64(x,26))|((~rotl64(x,49))&rotl64(x,32))) ^ rotl64(x,35));
    x = x ^ (((rotl64(x,46)&rotl64(x,51))|((~rotl64(x,46))&rotl64(x,43))) ^ rotl64(x,42));
    x ^= rotl64(key, 13);
    return x;
}
