#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// batch-53 hetMA5 schedule (triage z=9.18, andpos=4);
// the AND3 rotl(x,r) term is the b33 rc term (load-bearing).
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ (((rotl64(x,53)&rotl64(x,11))|((~rotl64(x,53))&rotl64(x,12))) ^ rotl64(x,21));
    x = x ^ (((rotl64(x,32)&rotl64(x,29))|((~rotl64(x,32))&rotl64(x,48))) ^ rotl64(x,44));
    x = x ^ (((rotl64(x,1)&rotl64(x,50))|((~rotl64(x,1))&rotl64(x,35))) ^ rotl64(x,39));
    x = x ^ (((rotl64(x,37)&rotl64(x,63))|((~rotl64(x,37))&rotl64(x,16))) ^ rotl64(x,17));
    x = x ^ (rotl64(x,46) & rotl64(x,45)) ^ rotl64(x,55);
    x ^= rotl64(key, 13);
    return x;
}
