#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-57 muxD5f schedule (fisher triage z=5.38 n_reject=0);
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,32)&rotl64(x,24))|((~rotl64(x,32))&rotl64(x,51))) ^ rotl64(x,27));
    x = x ^ (((rotl64(x,44)&rotl64(x,13))|((~rotl64(x,44))&rotl64(x,7))) ^ rotl64(x,53));
    x = x ^ (((rotl64(x,47)&rotl64(x,62))|((~rotl64(x,47))&rotl64(x,32))) ^ rotl64(x,42));
    x = x ^ (((rotl64(x,19)&rotl64(x,59))|((~rotl64(x,19))&rotl64(x,53))) ^ rotl64(x,42));
    x = x ^ (((rotl64(x,30)&rotl64(x,40))|((~rotl64(x,30))&rotl64(x,42))) ^ rotl64(x,1));
    x ^= rotl64(key, 13);
    return x;
}
