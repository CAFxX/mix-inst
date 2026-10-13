#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
// wave-38 stratified sample 6-stage AND schedule w38_t004 (triage z=9.930)
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    x ^= (rotl64(x,30) & rotl64(x,18)) ^ rotl64(x,10);
    x ^= (rotl64(x,61) & rotl64(x,63)) ^ rotl64(x,28);
    x ^= (rotl64(x,63) & rotl64(x,24)) ^ rotl64(x,45);
    x ^= (rotl64(x,13) & rotl64(x,30)) ^ rotl64(x,25);
    x ^= (rotl64(x,28) & rotl64(x,9)) ^ rotl64(x,28);
    x ^= (rotl64(x,40) & rotl64(x,16)) ^ rotl64(x,55);
    x ^= rotl64(key, 13);
    return x;
}
