#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=3.71 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,59)&rotl64(x,36))|((~rotl64(x,59))&rotl64(x,60))) ^ rotl64(x,31));
    x = x ^ (((rotl64(x,15)&rotl64(x,29))|((~rotl64(x,15))&rotl64(x,17))) ^ rotl64(x,45));
    x = x ^ (((rotl64(x,37)&rotl64(x,58))|((~rotl64(x,37))&rotl64(x,12))) ^ rotl64(x,27));
    x = x ^ (((rotl64(x,40)&rotl64(x,60))|((~rotl64(x,40))&rotl64(x,50))) ^ rotl64(x,8));
    x = x ^ (((rotl64(x,15)&rotl64(x,32))|((~rotl64(x,15))&rotl64(x,46))) ^ rotl64(x,25));
    x ^= rotl64(key, 13);
    return x;
}
