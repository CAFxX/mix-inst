// Fused candidate fz_majx_4: 4-stage: x ^= maj3(x,ra,rb) ^ maj3(rc,rd,re) ^ maj3(rf,rg,rh)
#include <stdint.h>
static uint64_t rotl64(uint64_t x, int r) {
    r &= 63; if (!r) return x;
    return (x << r) | (x >> (64 - r));
}
static uint64_t maj3(uint64_t a, uint64_t b, uint64_t c) {
    return (a&b)|(a&c)|(b&c);
}
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x ^= maj3(x, rotl64(x,7), rotl64(x,13))
         ^ maj3(rotl64(x,29), rotl64(x,41), rotl64(x,53))
         ^ maj3(rotl64(x,5), rotl64(x,23), rotl64(x,37));
    x ^= maj3(x, rotl64(x,11), rotl64(x,19))
         ^ maj3(rotl64(x,37), rotl64(x,47), rotl64(x,59))
         ^ maj3(rotl64(x,9), rotl64(x,31), rotl64(x,43));
    x ^= maj3(x, rotl64(x,17), rotl64(x,23))
         ^ maj3(rotl64(x,43), rotl64(x,51), rotl64(x,61))
         ^ maj3(rotl64(x,13), rotl64(x,35), rotl64(x,49));
    x ^= maj3(x, rotl64(x,5), rotl64(x,29))
         ^ maj3(rotl64(x,33), rotl64(x,45), rotl64(x,57))
         ^ maj3(rotl64(x,11), rotl64(x,27), rotl64(x,39));
    x ^= rotl64(k, 13);
    return x;
}
