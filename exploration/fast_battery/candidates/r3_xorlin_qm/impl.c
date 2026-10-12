/* r3_xorlin_qm reference implementation for the fast staged battery.
 * 4-round SPN, QM-minimized PRESENT S-box; bit-identical to
 * models/spn4_xorlin_1137.py :: mix_spn4_xorlin_1137_scalar.
 *   x = val ^ key
 *   repeat 4: x ^= rk[i]; PRESENT S-box on all 16 nibbles;
 *             x ^= ROTL64(x,11) ^ ROTL64(x,37)
 *   out = x ^ rk[4];  rk[i] = ROTL64(key,13*(i+1)) ^ ((i+1)*GOLDEN)
 */
#include <stdint.h>

static const uint8_t SBOX[16] =
    {0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2};
static const uint64_t GOLDEN = 0x9E3779B97F4A7C15ULL;

static uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}

static uint64_t rk(uint64_t key, int i) { /* i = 1..5 */
    return rotl64(key, 13u*(unsigned)i) ^ ((uint64_t)i * GOLDEN);
}

static uint64_t sbox16(uint64_t x) {
    uint64_t y = 0;
    for (int b = 0; b < 16; b++)
        y |= (uint64_t)SBOX[(x >> (4*b)) & 0xF] << (4*b);
    return y;
}

uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    for (int i = 1; i <= 4; i++) {
        uint64_t y = sbox16(x ^ rk(key, i));
        x = y ^ rotl64(y, 11) ^ rotl64(y, 37);
    }
    return x ^ rk(key, 5);
}
