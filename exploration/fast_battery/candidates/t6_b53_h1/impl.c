#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-53 hetMA5 schedule (triage z=3.01, andpos=3);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,48)&rotl64(x,6))|((~rotl64(x,48))&rotl64(x,49))) ^ rotl64(x,38));
    x = x ^ (((rotl64(x,31)&rotl64(x,3))|((~rotl64(x,31))&rotl64(x,6))) ^ rotl64(x,36));
    x = x ^ (((rotl64(x,44)&rotl64(x,33))|((~rotl64(x,44))&rotl64(x,56))) ^ rotl64(x,32));
    x = x ^ (rotl64(x,20) & rotl64(x,42)) ^ rotl64(x,19);
    x = x ^ (((rotl64(x,16)&rotl64(x,31))|((~rotl64(x,16))&rotl64(x,34))) ^ rotl64(x,13));
    x ^= rotl64(key, 13);
    return x;
}
