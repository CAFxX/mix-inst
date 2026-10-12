#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    // trichi stages
    const int tri[2][7] = {{1,2,4,8,16,32,7},{3,9,13,19,29,5,11}};
    for (int i = 0; i < 2; i++) {
        uint64_t r0=rotl64(x,tri[i][0]), r1=rotl64(x,tri[i][1]), r2=rotl64(x,tri[i][2]);
        uint64_t r3=rotl64(x,tri[i][3]), r4=rotl64(x,tri[i][4]), r5=rotl64(x,tri[i][5]);
        uint64_t r6=rotl64(x,tri[i][6]);
        x ^= ((~r0) & r1) ^ ((~r2) & r3) ^ ((~r4) & r5) ^ r6;
    }
    // chi stages
    const int chi[2][3] = {{11,23,37},{19,41,23}};
    for (int i = 0; i < 2; i++) {
        uint64_t r0=rotl64(x,chi[i][0]), r1=rotl64(x,chi[i][1]), r2=rotl64(x,chi[i][2]);
        x ^= ((~r0) & r1) ^ r2;
    }
    x ^= rotl64(key, 13);
    return x;
}
