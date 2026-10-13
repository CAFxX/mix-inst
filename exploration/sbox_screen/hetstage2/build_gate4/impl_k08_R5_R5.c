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
// hetstage2 gate4 k08_R5_R5
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x = x ^ rotl64(x,53) ^ rotl64(x,54);
    x = x ^ (((rotl64(x,37)&rotl64(x,54))|((~rotl64(x,37))&rotl64(x,29))) ^ rotl64(x,26));
    x = x ^ (((rotl64(x,59)&rotl64(x,8))|((~rotl64(x,59))&rotl64(x,54))) ^ rotl64(x,21));
    x = x ^ (((rotl64(x,25)&rotl64(x,38))|((~rotl64(x,25))&rotl64(x,34))) ^ rotl64(x,6));
    x = x ^ (((rotl64(x,18)&rotl64(x,56))|((~rotl64(x,18))&rotl64(x,22))) ^ rotl64(x,49));
    x ^= rotl64(key, 13);
    return x;
}
