#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=3.92 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,1)&rotl64(x,14))|((~rotl64(x,1))&rotl64(x,60))) ^ rotl64(x,19));
    x = x ^ (((rotl64(x,4)&rotl64(x,38))|((~rotl64(x,4))&rotl64(x,32))) ^ rotl64(x,39));
    x = x ^ (((rotl64(x,26)&rotl64(x,57))|((~rotl64(x,26))&rotl64(x,39))) ^ rotl64(x,31));
    x = x ^ (((rotl64(x,62)&rotl64(x,32))|((~rotl64(x,62))&rotl64(x,53))) ^ rotl64(x,26));
    x = x ^ (((rotl64(x,24)&rotl64(x,16))|((~rotl64(x,24))&rotl64(x,40))) ^ rotl64(x,4));
    x ^= rotl64(key, 13);
    return x;
}
