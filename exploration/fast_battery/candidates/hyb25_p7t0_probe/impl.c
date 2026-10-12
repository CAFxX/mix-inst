#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// hyb25_p7t0_probe: batch-25 PNL 7-stage (triage z=2.92)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= ((rotl64(x,7) & rotl64(x,49)) & 0x00000000ffffffffULL) ^ rotl64(x,3) ^ rotl64(x,34);
    x ^= ((rotl64(x,6) & rotl64(x,15)) & 0x0f0f0f0f0f0f0f0fULL) ^ rotl64(x,7) ^ rotl64(x,16);
    x ^= ((rotl64(x,38) & rotl64(x,42)) & 0x5555555555555555ULL) ^ rotl64(x,57) ^ rotl64(x,12);
    x ^= ((rotl64(x,23) & rotl64(x,13)) & 0xaaaaaaaaaaaaaaaaULL) ^ rotl64(x,57) ^ rotl64(x,29);
    x ^= ((rotl64(x,59) & rotl64(x,48)) & 0xffff0000ffff0000ULL) ^ rotl64(x,24) ^ rotl64(x,23);
    x ^= ((rotl64(x,23) & rotl64(x,42)) & 0x00000000ffffffffULL) ^ rotl64(x,50) ^ rotl64(x,34);
    x ^= ((rotl64(x,15) & rotl64(x,63)) & 0xccccccccccccccccULL) ^ rotl64(x,48) ^ rotl64(x,37);
    x ^= rotl64(key, 13);
    return x;
}
