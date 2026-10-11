#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
static inline uint64_t bitrev64(uint64_t x) {
    x = ((x & 0x5555555555555555ULL) << 1)  | ((x >> 1)  & 0x5555555555555555ULL);
    x = ((x & 0x3333333333333333ULL) << 2)  | ((x >> 2)  & 0x3333333333333333ULL);
    x = ((x & 0x0f0f0f0f0f0f0f0fULL) << 4)  | ((x >> 4)  & 0x0f0f0f0f0f0f0f0fULL);
    x = ((x & 0x00ff00ff00ff00ffULL) << 8)  | ((x >> 8)  & 0x00ff00ff00ff00ffULL);
    x = ((x & 0x0000ffff0000ffffULL) << 16) | ((x >> 16) & 0x0000ffff0000ffffULL);
    return (x << 32) | (x >> 32);
}
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x ^= (rotl64(x,1) & rotl64(x,2)) ^ rotl64(x,13);
    x ^= (rotl64(x,7) & rotl64(x,19)) ^ rotl64(x,5);
    x = bitrev64(x);
    x ^= (rotl64(x,3) & rotl64(x,11)) ^ rotl64(x,29);
    x ^= (rotl64(x,17) & rotl64(x,31)) ^ rotl64(x,7);
    x = bitrev64(x);
    x ^= (rotl64(x,11) & rotl64(x,23)) ^ rotl64(x,37);
    x ^= rotl64(k, 13);
    return x;
}
