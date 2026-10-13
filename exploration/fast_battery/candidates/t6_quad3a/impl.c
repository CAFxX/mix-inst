#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {
    r &= 63; return r ? (x << r) | (x >> (64 - r)) : x;
}
static inline uint32_t rotl32(uint32_t x, int r) {
    r &= 31; return r ? (x << r) | (x >> (32 - r)) : x;
}
static inline uint16_t rotl16(uint16_t x, int r) {
    r &= 15; return r ? (uint16_t)(((uint32_t)x << r) | ((uint32_t)x >> (16 - r))) : x;
}
static const uint64_t RC[8] = {0x9E3779B97F4A7C15u, 0x3C6EF372FE94F82Au, 0xDAA66D2C7DDF743Fu, 0x78DDE6E5FD29F054u, 0x2545F4914F6CDD1Du, 0x9E3779B9A1E7C2FAu, 0x3C6EF372ECA0AE52u, 0xDAA66D2CD6129B3Eu};
static const uint8_t SB0[16] = {0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6};
static inline uint64_t rk(uint64_t key, int j) { return rotl64(key, 13*(j+1)) ^ RC[j % 8]; }

// t6_quad3a: 3 super-stages, 4 parallel 16-bit cascades + cross
uint64_t mix_hash(uint64_t val, uint64_t key) {
    uint64_t x = val ^ key;
    uint16_t l[4], n[4];
    l[0]=(uint16_t)x; l[1]=(uint16_t)(x>>16); l[2]=(uint16_t)(x>>32); l[3]=(uint16_t)(x>>48);
    l[0] ^= (rotl16(l[0],3) & rotl16(l[0],9)) ^ rotl16(l[0],13) ^ (uint16_t)rk(key,0);
    l[1] ^= (rotl16(l[1],8) & rotl16(l[1],14)) ^ rotl16(l[1],2) ^ (uint16_t)rk(key,0);
    l[2] ^= (rotl16(l[2],13) & rotl16(l[2],3)) ^ rotl16(l[2],7) ^ (uint16_t)rk(key,0);
    l[3] ^= (rotl16(l[3],2) & rotl16(l[3],8)) ^ rotl16(l[3],12) ^ (uint16_t)rk(key,0);
    l[0] ^= (rotl16(l[0],7) & rotl16(l[0],2)) ^ rotl16(l[0],11) ^ (uint16_t)rk(key,1);
    l[1] ^= (rotl16(l[1],12) & rotl16(l[1],7)) ^ rotl16(l[1],0) ^ (uint16_t)rk(key,1);
    l[2] ^= (rotl16(l[2],1) & rotl16(l[2],12)) ^ rotl16(l[2],5) ^ (uint16_t)rk(key,1);
    l[3] ^= (rotl16(l[3],6) & rotl16(l[3],1)) ^ rotl16(l[3],10) ^ (uint16_t)rk(key,1);
    n[0] = l[0] ^ rotl16(l[1],3) ^ rotl16(l[2],7) ^ (uint16_t)rk(key,6);
    n[1] = l[1] ^ rotl16(l[2],3) ^ rotl16(l[3],7) ^ (uint16_t)rk(key,7);
    n[2] = l[2] ^ rotl16(l[3],3) ^ rotl16(l[0],7) ^ (uint16_t)rk(key,8);
    n[3] = l[3] ^ rotl16(l[0],3) ^ rotl16(l[1],7) ^ (uint16_t)rk(key,9);
    x = (uint64_t)n[0] | ((uint64_t)n[1] << 16) | ((uint64_t)n[2] << 32) | ((uint64_t)n[3] << 48);
    l[0]=(uint16_t)x; l[1]=(uint16_t)(x>>16); l[2]=(uint16_t)(x>>32); l[3]=(uint16_t)(x>>48);
    l[0] ^= (rotl16(l[0],11) & rotl16(l[0],5)) ^ rotl16(l[0],1) ^ (uint16_t)rk(key,2);
    l[1] ^= (rotl16(l[1],0) & rotl16(l[1],10)) ^ rotl16(l[1],6) ^ (uint16_t)rk(key,2);
    l[2] ^= (rotl16(l[2],5) & rotl16(l[2],15)) ^ rotl16(l[2],11) ^ (uint16_t)rk(key,2);
    l[3] ^= (rotl16(l[3],10) & rotl16(l[3],4)) ^ rotl16(l[3],0) ^ (uint16_t)rk(key,2);
    l[0] ^= (rotl16(l[0],13) & rotl16(l[0],8)) ^ rotl16(l[0],4) ^ (uint16_t)rk(key,3);
    l[1] ^= (rotl16(l[1],2) & rotl16(l[1],13)) ^ rotl16(l[1],9) ^ (uint16_t)rk(key,3);
    l[2] ^= (rotl16(l[2],7) & rotl16(l[2],2)) ^ rotl16(l[2],14) ^ (uint16_t)rk(key,3);
    l[3] ^= (rotl16(l[3],12) & rotl16(l[3],7)) ^ rotl16(l[3],3) ^ (uint16_t)rk(key,3);
    n[0] = l[0] ^ rotl16(l[1],5) ^ rotl16(l[2],11) ^ (uint16_t)rk(key,8);
    n[1] = l[1] ^ rotl16(l[2],5) ^ rotl16(l[3],11) ^ (uint16_t)rk(key,9);
    n[2] = l[2] ^ rotl16(l[3],5) ^ rotl16(l[0],11) ^ (uint16_t)rk(key,10);
    n[3] = l[3] ^ rotl16(l[0],5) ^ rotl16(l[1],11) ^ (uint16_t)rk(key,11);
    x = (uint64_t)n[0] | ((uint64_t)n[1] << 16) | ((uint64_t)n[2] << 32) | ((uint64_t)n[3] << 48);
    l[0]=(uint16_t)x; l[1]=(uint16_t)(x>>16); l[2]=(uint16_t)(x>>32); l[3]=(uint16_t)(x>>48);
    l[0] ^= (rotl16(l[0],6) & rotl16(l[0],12)) ^ rotl16(l[0],2) ^ (uint16_t)rk(key,4);
    l[1] ^= (rotl16(l[1],11) & rotl16(l[1],1)) ^ rotl16(l[1],7) ^ (uint16_t)rk(key,4);
    l[2] ^= (rotl16(l[2],0) & rotl16(l[2],6)) ^ rotl16(l[2],12) ^ (uint16_t)rk(key,4);
    l[3] ^= (rotl16(l[3],5) & rotl16(l[3],11)) ^ rotl16(l[3],1) ^ (uint16_t)rk(key,4);
    l[0] ^= (rotl16(l[0],9) & rotl16(l[0],4)) ^ rotl16(l[0],14) ^ (uint16_t)rk(key,5);
    l[1] ^= (rotl16(l[1],14) & rotl16(l[1],9)) ^ rotl16(l[1],3) ^ (uint16_t)rk(key,5);
    l[2] ^= (rotl16(l[2],3) & rotl16(l[2],14)) ^ rotl16(l[2],8) ^ (uint16_t)rk(key,5);
    l[3] ^= (rotl16(l[3],8) & rotl16(l[3],3)) ^ rotl16(l[3],13) ^ (uint16_t)rk(key,5);
    n[0] = l[0] ^ rotl16(l[1],9) ^ rotl16(l[2],13) ^ (uint16_t)rk(key,10);
    n[1] = l[1] ^ rotl16(l[2],9) ^ rotl16(l[3],13) ^ (uint16_t)rk(key,11);
    n[2] = l[2] ^ rotl16(l[3],9) ^ rotl16(l[0],13) ^ (uint16_t)rk(key,12);
    n[3] = l[3] ^ rotl16(l[0],9) ^ rotl16(l[1],13) ^ (uint16_t)rk(key,13);
    x = (uint64_t)n[0] | ((uint64_t)n[1] << 16) | ((uint64_t)n[2] << 32) | ((uint64_t)n[3] << 48);
    x ^= rotl64(key, 13) >> 32;
    return x;
}
