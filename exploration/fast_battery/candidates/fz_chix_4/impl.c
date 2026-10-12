// Fused candidate fz_chix_4: 4-stage: x ^= ((~x)&ra) ^ ((~rb)&rc) ^ ((~rd)&re)
#include <stdint.h>
static uint64_t rotl64(uint64_t x, int r) {
    r &= 63; if (!r) return x;
    return (x << r) | (x >> (64 - r));
}
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x ^= ((~x)&rotl64(x,7)) ^ ((~rotl64(x,13))&rotl64(x,29)) ^ ((~rotl64(x,41))&rotl64(x,53));
    x ^= ((~x)&rotl64(x,11)) ^ ((~rotl64(x,19))&rotl64(x,37)) ^ ((~rotl64(x,47))&rotl64(x,59));
    x ^= ((~x)&rotl64(x,17)) ^ ((~rotl64(x,23))&rotl64(x,43)) ^ ((~rotl64(x,51))&rotl64(x,61));
    x ^= ((~x)&rotl64(x,5)) ^ ((~rotl64(x,29))&rotl64(x,33)) ^ ((~rotl64(x,45))&rotl64(x,57));
    x ^= rotl64(k, 13);
    return x;
}
