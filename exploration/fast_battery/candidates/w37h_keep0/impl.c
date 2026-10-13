#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63;
    return r ? (uint64_t)((x << r) | (x >> (64 - r))) : x;
}

uint64_t mix_w37h_keep0(uint64_t x, uint64_t key) {
    x ^= key;
    x = x ^ (rotl64(x, 26) & rotl64(x, 35)) ^ rotl64(x, 18) ^ rotl64(x, 52) ^ rotl64(x, 2);  /* stage 1 */
    x = x ^ (rotl64(x, 56) & rotl64(x, 26)) ^ rotl64(x, 60) ^ rotl64(x, 42) ^ rotl64(x, 19);  /* stage 2 */
    x = x ^ (rotl64(x, 62) & rotl64(x, 50)) ^ rotl64(x, 33) ^ rotl64(x, 45) ^ rotl64(x, 11);  /* stage 3 */
    x = x ^ (rotl64(x, 3) & rotl64(x, 41)) ^ rotl64(x, 47) ^ rotl64(x, 14) ^ rotl64(x, 54);  /* stage 4 */
    x = x ^ (rotl64(x, 29) & rotl64(x, 26)) ^ rotl64(x, 59) ^ rotl64(x, 23) ^ rotl64(x, 62);  /* stage 5 */
    return x ^ rotl64(key, 13);
}
