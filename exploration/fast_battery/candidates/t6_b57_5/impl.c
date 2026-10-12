#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=3.22 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,26)&rotl64(x,41))|((~rotl64(x,26))&rotl64(x,43))) ^ rotl64(x,31));
    x = x ^ (((rotl64(x,29)&rotl64(x,28))|((~rotl64(x,29))&rotl64(x,9))) ^ rotl64(x,34));
    x = x ^ (((rotl64(x,3)&rotl64(x,11))|((~rotl64(x,3))&rotl64(x,32))) ^ rotl64(x,58));
    x = x ^ (((rotl64(x,35)&rotl64(x,25))|((~rotl64(x,35))&rotl64(x,8))) ^ rotl64(x,30));
    x = x ^ (((rotl64(x,1)&rotl64(x,40))|((~rotl64(x,1))&rotl64(x,20))) ^ rotl64(x,23));
    x ^= rotl64(key, 13);
    return x;
}
