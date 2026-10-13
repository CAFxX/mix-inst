#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-61 muxD5f schedule (fisher triage z=2.55 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,17)&rotl64(x,13))|((~rotl64(x,17))&rotl64(x,52))) ^ rotl64(x,55));
    x = x ^ (((rotl64(x,63)&rotl64(x,62))|((~rotl64(x,63))&rotl64(x,51))) ^ rotl64(x,41));
    x = x ^ (((rotl64(x,29)&rotl64(x,25))|((~rotl64(x,29))&rotl64(x,35))) ^ rotl64(x,24));
    x = x ^ (((rotl64(x,9)&rotl64(x,4))|((~rotl64(x,9))&rotl64(x,49))) ^ rotl64(x,36));
    x = x ^ (((rotl64(x,16)&rotl64(x,54))|((~rotl64(x,16))&rotl64(x,52))) ^ rotl64(x,34));
    x ^= rotl64(key, 13);
    return x;
}
