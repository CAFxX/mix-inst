#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=2.55 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,11)&rotl64(x,59))|((~rotl64(x,11))&rotl64(x,39))) ^ rotl64(x,13));
    x = x ^ (((rotl64(x,9)&rotl64(x,27))|((~rotl64(x,9))&rotl64(x,21))) ^ rotl64(x,41));
    x = x ^ (((rotl64(x,47)&rotl64(x,20))|((~rotl64(x,47))&rotl64(x,30))) ^ rotl64(x,22));
    x = x ^ (((rotl64(x,59)&rotl64(x,29))|((~rotl64(x,59))&rotl64(x,13))) ^ rotl64(x,45));
    x = x ^ (((rotl64(x,39)&rotl64(x,18))|((~rotl64(x,39))&rotl64(x,24))) ^ rotl64(x,61));
    x ^= rotl64(key, 13);
    return x;
}
