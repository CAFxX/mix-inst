#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-62 prescreen calib-570
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,13)&rotl64(x,15))|((~rotl64(x,13))&rotl64(x,12))) ^ rotl64(x,43));
    x = x ^ (((rotl64(x,32)&rotl64(x,55))|((~rotl64(x,32))&rotl64(x,29))) ^ rotl64(x,11));
    x = x ^ (((rotl64(x,17)&rotl64(x,58))|((~rotl64(x,17))&rotl64(x,27))) ^ rotl64(x,26));
    x = x ^ (((rotl64(x,42)&rotl64(x,27))|((~rotl64(x,42))&rotl64(x,57))) ^ rotl64(x,8));
    x = x ^ (((rotl64(x,44)&rotl64(x,59))|((~rotl64(x,44))&rotl64(x,3))) ^ rotl64(x,7));
    x ^= rotl64(key, 13);
    return x;
}
