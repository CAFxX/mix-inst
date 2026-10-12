// Single-addition ARX, pba19 (track-6 ARX axis; impl written 2026-10-10 from model.py).
// x = val + key; x ^= rotl(x,13) ^ rotl(x,29); x = P(x); x ^= rotl(x,7); x ^= key
// PBOX[i] = (19*i + 1) % 64
#include <stdint.h>

static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}

static inline uint64_t pbox64(uint64_t x) {
    uint64_t y = 0;
    for (int i = 0; i < 64; i++) {
        y |= ((x >> i) & 1ULL) << ((19 * i + 1) & 63);
    }
    return y;
}

uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val + key;
    x ^= rotl64(x, 13) ^ rotl64(x, 29);
    x = pbox64(x);
    x ^= rotl64(x, 7);
    x ^= key;
    return x;
}
