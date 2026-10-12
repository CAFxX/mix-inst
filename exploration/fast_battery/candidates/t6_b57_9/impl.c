#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=3.81 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,19)&rotl64(x,21))|((~rotl64(x,19))&rotl64(x,17))) ^ rotl64(x,2));
    x = x ^ (((rotl64(x,3)&rotl64(x,36))|((~rotl64(x,3))&rotl64(x,41))) ^ rotl64(x,27));
    x = x ^ (((rotl64(x,34)&rotl64(x,60))|((~rotl64(x,34))&rotl64(x,43))) ^ rotl64(x,18));
    x = x ^ (((rotl64(x,47)&rotl64(x,17))|((~rotl64(x,47))&rotl64(x,52))) ^ rotl64(x,22));
    x = x ^ (((rotl64(x,58)&rotl64(x,63))|((~rotl64(x,58))&rotl64(x,56))) ^ rotl64(x,50));
    x ^= rotl64(key, 13);
    return x;
}
