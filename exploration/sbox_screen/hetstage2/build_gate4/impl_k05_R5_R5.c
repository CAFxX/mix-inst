#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint64_t gfmul_c(uint64_t x, uint64_t C) {
    /* carryless multiply x*C, reduce mod z^64+z^4+z^3+z+1 */
    __uint128_t p = 0;
    uint64_t cc = C; int b = 0;
    while (cc) { if (cc & 1) p ^= (__uint128_t)x << b;
                 cc >>= 1; b++; }
    for (int i = 127; i >= 64; i--)
        if ((p >> i) & 1) p ^= (__uint128_t)0x1BU << (i - 64);
    return (uint64_t)p;
}
// hetstage2 gate4 k05_R5_R5
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,2) ^ rotl64(x,59);
    x = x ^ (((rotl64(x,56)&rotl64(x,54))|((~rotl64(x,56))&rotl64(x,27))) ^ rotl64(x,31));
    x = x ^ (((rotl64(x,62)&rotl64(x,56))|((~rotl64(x,62))&rotl64(x,21))) ^ rotl64(x,34));
    x = x ^ (((rotl64(x,61)&rotl64(x,6))|((~rotl64(x,61))&rotl64(x,19))) ^ rotl64(x,11));
    x = x ^ (((rotl64(x,44)&rotl64(x,52))|((~rotl64(x,44))&rotl64(x,24))) ^ rotl64(x,46));
    x ^= rotl64(key, 13);
    return x;
}
