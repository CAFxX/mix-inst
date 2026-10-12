#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-54 hetMA5p1 schedule (triage z=7.27, andpos=1);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,44)&rotl64(x,46))|((~rotl64(x,44))&rotl64(x,21))) ^ rotl64(x,14));
    x = x ^ (rotl64(x,16) & rotl64(x,55)) ^ rotl64(x,3);
    x = x ^ (((rotl64(x,19)&rotl64(x,23))|((~rotl64(x,19))&rotl64(x,12))) ^ rotl64(x,36));
    x = x ^ (((rotl64(x,44)&rotl64(x,63))|((~rotl64(x,44))&rotl64(x,14))) ^ rotl64(x,2));
    x = x ^ (((rotl64(x,17)&rotl64(x,22))|((~rotl64(x,17))&rotl64(x,58))) ^ rotl64(x,43));
    x ^= rotl64(key, 13);
    return x;
}
