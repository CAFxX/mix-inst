#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-53 hetMA5 schedule (triage z=2.95, andpos=1);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,28)&rotl64(x,29))|((~rotl64(x,28))&rotl64(x,16))) ^ rotl64(x,37));
    x = x ^ (rotl64(x,16) & rotl64(x,10)) ^ rotl64(x,5);
    x = x ^ (((rotl64(x,14)&rotl64(x,17))|((~rotl64(x,14))&rotl64(x,40))) ^ rotl64(x,61));
    x = x ^ (((rotl64(x,11)&rotl64(x,50))|((~rotl64(x,11))&rotl64(x,35))) ^ rotl64(x,20));
    x = x ^ (((rotl64(x,23)&rotl64(x,10))|((~rotl64(x,23))&rotl64(x,31))) ^ rotl64(x,24));
    x ^= rotl64(key, 13);
    return x;
}
