#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-54 hetMA5p1 schedule (triage z=4.58, andpos=1);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,24)&rotl64(x,40))|((~rotl64(x,24))&rotl64(x,21))) ^ rotl64(x,2));
    x = x ^ (rotl64(x,34) & rotl64(x,46)) ^ rotl64(x,29);
    x = x ^ (((rotl64(x,31)&rotl64(x,57))|((~rotl64(x,31))&rotl64(x,17))) ^ rotl64(x,11));
    x = x ^ (((rotl64(x,28)&rotl64(x,21))|((~rotl64(x,28))&rotl64(x,14))) ^ rotl64(x,45));
    x = x ^ (((rotl64(x,7)&rotl64(x,27))|((~rotl64(x,7))&rotl64(x,63))) ^ rotl64(x,48));
    x ^= rotl64(key, 13);
    return x;
}
