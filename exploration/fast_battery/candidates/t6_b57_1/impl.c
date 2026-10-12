#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=2.41 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,20)&rotl64(x,37))|((~rotl64(x,20))&rotl64(x,54))) ^ rotl64(x,24));
    x = x ^ (((rotl64(x,63)&rotl64(x,45))|((~rotl64(x,63))&rotl64(x,11))) ^ rotl64(x,49));
    x = x ^ (((rotl64(x,38)&rotl64(x,50))|((~rotl64(x,38))&rotl64(x,18))) ^ rotl64(x,16));
    x = x ^ (((rotl64(x,46)&rotl64(x,45))|((~rotl64(x,46))&rotl64(x,27))) ^ rotl64(x,16));
    x = x ^ (((rotl64(x,62)&rotl64(x,47))|((~rotl64(x,62))&rotl64(x,3))) ^ rotl64(x,37));
    x ^= rotl64(key, 13);
    return x;
}
