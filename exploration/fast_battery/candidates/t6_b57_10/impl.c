#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=3.91 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,41)&rotl64(x,58))|((~rotl64(x,41))&rotl64(x,43))) ^ rotl64(x,14));
    x = x ^ (((rotl64(x,46)&rotl64(x,33))|((~rotl64(x,46))&rotl64(x,2))) ^ rotl64(x,16));
    x = x ^ (((rotl64(x,29)&rotl64(x,24))|((~rotl64(x,29))&rotl64(x,5))) ^ rotl64(x,52));
    x = x ^ (((rotl64(x,33)&rotl64(x,8))|((~rotl64(x,33))&rotl64(x,49))) ^ rotl64(x,20));
    x = x ^ (((rotl64(x,35)&rotl64(x,9))|((~rotl64(x,35))&rotl64(x,4))) ^ rotl64(x,36));
    x ^= rotl64(key, 13);
    return x;
}
