#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=2.73 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,17)&rotl64(x,22))|((~rotl64(x,17))&rotl64(x,10))) ^ rotl64(x,53));
    x = x ^ (((rotl64(x,63)&rotl64(x,62))|((~rotl64(x,63))&rotl64(x,49))) ^ rotl64(x,41));
    x = x ^ (((rotl64(x,29)&rotl64(x,39))|((~rotl64(x,29))&rotl64(x,35))) ^ rotl64(x,6));
    x = x ^ (((rotl64(x,9)&rotl64(x,4))|((~rotl64(x,9))&rotl64(x,44))) ^ rotl64(x,36));
    x = x ^ (((rotl64(x,5)&rotl64(x,54))|((~rotl64(x,5))&rotl64(x,31))) ^ rotl64(x,34));
    x ^= rotl64(key, 13);
    return x;
}
