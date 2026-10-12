#include <stdint.h>
/* fz22_maj4a */
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x; }
static inline uint64_t maj64(uint64_t a, uint64_t b, uint64_t c) {
    return (a & b) | (a & c) | (b & c); }
uint64_t mix_hash(uint64_t v, uint64_t k) {
    uint64_t x = v ^ k;
    x = x ^ maj64(x, rotl64(x,1), rotl64(x,7)) ^ rotl64(x,13);
    x = x ^ maj64(x, rotl64(x,5), rotl64(x,15)) ^ rotl64(x,25);
    x = x ^ maj64(x, rotl64(x,11), rotl64(x,23)) ^ rotl64(x,37);
    x = x ^ maj64(x, rotl64(x,17), rotl64(x,31)) ^ rotl64(x,47);
    return x;
}
