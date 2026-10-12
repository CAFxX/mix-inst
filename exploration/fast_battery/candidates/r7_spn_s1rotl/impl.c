/* r7_spn_s1rotl: 4-round 64-bit SPN.
 * Bit-exact vs Python model round7/models/r7d.py (r7_spn_s1rotl_np).
 * Round: S1 on 16 nibbles -> x ^ rotl64(x,7) ^ rotl64(x,13) -> ^rk64(i).
 * Whiten in/out with key.
 * NOTE: the originally proposed rotl64(x,29) term was dropped because the
 * 4-term rotation-XOR map is provably singular on 64 bits
 * (over GF(2), x^64+1 = (x+1)^64, so any even-term rotation sum has (x+1)
 * as a factor; measured rank 63). The 3-term map is always invertible.
 */
#include <stdint.h>

static const uint8_t S1[16] = {0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10};

static uint64_t rotl64(uint64_t x, int n) {
    n &= 63;
    return n ? (x << n) | (x >> (64 - n)) : x;
}

static uint64_t rk(uint64_t k, int i) {
    return rotl64(k, 13 * (i + 1)) ^ ((uint64_t)(i + 1) * 0x9E3779B97F4A7C15ULL);
}

static uint64_t sbox64(uint64_t x) {
    uint64_t r = 0;
    for (int j = 0; j < 16; j++)
        r |= (uint64_t)S1[(x >> (4 * j)) & 0xF] << (4 * j);
    return r;
}

uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    for (int i = 1; i <= 4; i++) {
        x = sbox64(x);
        x = x ^ rotl64(x, 7) ^ rotl64(x, 13);
        x ^= rk(key, i);
    }
    return x ^ key;
}
