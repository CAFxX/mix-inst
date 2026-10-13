#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, unsigned r) {
    r &= 63;
    return r ? (uint64_t)((x << r) | (x >> (64 - r))) : x;
}

uint64_t mix_w37h_keep1(uint64_t x, uint64_t key) {
    x ^= key;
    x = x ^ (rotl64(x, 30) & rotl64(x, 41)) ^ rotl64(x, 39) ^ rotl64(x, 51) ^ rotl64(x, 25);  /* stage 1 */
    x = x ^ (rotl64(x, 51) & rotl64(x, 39)) ^ rotl64(x, 15) ^ rotl64(x, 14) ^ rotl64(x, 37);  /* stage 2 */
    x = x ^ (rotl64(x, 47) & rotl64(x, 8)) ^ rotl64(x, 31) ^ rotl64(x, 24) ^ rotl64(x, 48);  /* stage 3 */
    x = x ^ (rotl64(x, 52) & rotl64(x, 53)) ^ rotl64(x, 18) ^ rotl64(x, 42) ^ rotl64(x, 63);  /* stage 4 */
    x = x ^ (rotl64(x, 34) & rotl64(x, 33)) ^ rotl64(x, 28) ^ rotl64(x, 36) ^ rotl64(x, 29);  /* stage 5 */
    return x ^ rotl64(key, 13);
}
