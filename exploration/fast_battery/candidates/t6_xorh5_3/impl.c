#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// xorh5 hetero schedule (fisher triage z=2.60 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,52)&rotl64(x,55))|((~rotl64(x,52))&rotl64(x,44))) ^ rotl64(x,35));
    x = x ^ (((rotl64(x,13)&rotl64(x,44))|((~rotl64(x,13))&rotl64(x,61))) ^ rotl64(x,4));
    x = x ^ (((rotl64(x,58)&rotl64(x,41))|((~rotl64(x,58))&rotl64(x,17))) ^ rotl64(x,42));
    x = x ^ (((rotl64(x,27)&rotl64(x,1))|((~rotl64(x,27))&rotl64(x,43))) ^ rotl64(x,61));
    x = x ^ rotl64(x,61) ^ rotl64(x,44) ^ rotl64(x,35) ^ rotl64(x,55);
    x ^= rotl64(key, 13);
    return x;
}
