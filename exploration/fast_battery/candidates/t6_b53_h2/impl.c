#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-53 hetMA5 schedule (triage z=6.45, andpos=0);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (rotl64(x,31) & rotl64(x,29)) ^ rotl64(x,60);
    x = x ^ (((rotl64(x,18)&rotl64(x,11))|((~rotl64(x,18))&rotl64(x,35))) ^ rotl64(x,55));
    x = x ^ (((rotl64(x,31)&rotl64(x,32))|((~rotl64(x,31))&rotl64(x,62))) ^ rotl64(x,42));
    x = x ^ (((rotl64(x,18)&rotl64(x,26))|((~rotl64(x,18))&rotl64(x,41))) ^ rotl64(x,25));
    x = x ^ (((rotl64(x,17)&rotl64(x,38))|((~rotl64(x,17))&rotl64(x,56))) ^ rotl64(x,22));
    x ^= rotl64(key, 13);
    return x;
}
