#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=3.67 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,11)&rotl64(x,8))|((~rotl64(x,11))&rotl64(x,23))) ^ rotl64(x,29));
    x = x ^ (((rotl64(x,24)&rotl64(x,10))|((~rotl64(x,24))&rotl64(x,6))) ^ rotl64(x,61));
    x = x ^ (((rotl64(x,37)&rotl64(x,26))|((~rotl64(x,37))&rotl64(x,56))) ^ rotl64(x,63));
    x = x ^ (((rotl64(x,49)&rotl64(x,28))|((~rotl64(x,49))&rotl64(x,52))) ^ rotl64(x,46));
    x = x ^ (((rotl64(x,58)&rotl64(x,28))|((~rotl64(x,58))&rotl64(x,54))) ^ rotl64(x,3));
    x ^= rotl64(key, 13);
    return x;
}
