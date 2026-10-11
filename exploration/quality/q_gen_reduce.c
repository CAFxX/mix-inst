/* Q2 v2: PractRand reduction-stream generator with input sequences.
 * Usage: ./qgen <key_hex> <nbytes> <seq> <red>
 *   seq: s1|s8|s256|s4k|s64k|s4g  ->  v = i * stride, stride in
 *         {1, 8, 256, 4096, 65536, 4294967296}. Power-of-two strides pin
 *         low input bits to zero (aligned-data pathology).
 *   red: low8|low16|low32|high32|xor32|lemire1e9p7|mod1e9p7|mod1000
 *     low8       : x & 0xFF -> 1 byte/val
 *     low16      : x & 0xFFFF -> 2 bytes LE/val
 *     low32      : x & 0xFFFFFFFF -> 4 bytes LE/val
 *     high32     : x >> 32 -> 4 bytes LE/val
 *     xor32      : (x&0xFFFFFFFF)^(x>>32) -> 4 bytes LE/val
 *     lemire1e9p7: ((unsigned __int128)x * 1000000007) >> 64 -> 4 bytes LE/val
 *     mod1e9p7  : x % 1000000007 -> 4 bytes LE/val
 *     mod1000    : x % 1000 -> 2 bytes LE/val
 * Compiled per-candidate with candidates/<name>/impl.c defining mix_hash.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

uint64_t mix_hash(uint64_t val, uint64_t key);

int main(int argc, char **argv) {
    if (argc < 5) {
        fprintf(stderr, "usage: qgen <key_hex> <nbytes> <s1|s8|s256|s4k|s64k|s4g> "
                        "<low8|low16|low32|high32|xor32|lemire1e9p7|mod1e9p7|mod1000>\n");
        return 1;
    }
    uint64_t key = strtoull(argv[1], NULL, 16);
    unsigned long long nbytes = strtoull(argv[2], NULL, 10);
    const char *seq = argv[3];
    const char *red = argv[4];

    uint64_t stride;
    if (!strcmp(seq, "s1")) stride = 1ULL;
    else if (!strcmp(seq, "s8")) stride = 8ULL;
    else if (!strcmp(seq, "s256")) stride = 256ULL;
    else if (!strcmp(seq, "s4k")) stride = 4096ULL;
    else if (!strcmp(seq, "s64k")) stride = 65536ULL;
    else if (!strcmp(seq, "s4g")) stride = 4294967296ULL;
    else { fprintf(stderr, "bad seq %s\n", seq); return 1; }

    int wpb; /* bytes per val */
    if (!strcmp(red, "low8")) wpb = 1;
    else if (!strcmp(red, "low16") || !strcmp(red, "mod1000")) wpb = 2;
    else if (!strcmp(red, "low32") || !strcmp(red, "high32") || !strcmp(red, "xor32") ||
             !strcmp(red, "lemire1e9p7") || !strcmp(red, "mod1e9p7")) wpb = 4;
    else { fprintf(stderr, "bad red %s\n", red); return 1; }

    unsigned long long nvals = (nbytes + wpb - 1) / wpb;
    static uint8_t buf[1 << 20];
    unsigned long long done = 0, emitted = 0;
    while (done < nvals && emitted < nbytes) {
        unsigned long long m = nvals - done;
        if (m > ((1 << 20) / 8)) m = (1 << 20) / 8;
        unsigned long long bi = 0;
        for (unsigned long long i = 0; i < m; i++) {
            uint64_t v = (done + i) * stride;
            uint64_t x = mix_hash(v, key);
            uint32_t r;
            if (!strcmp(red, "low8")) r = (uint32_t)(x & 0xFF);
            else if (!strcmp(red, "low16")) r = (uint32_t)(x & 0xFFFF);
            else if (!strcmp(red, "low32")) r = (uint32_t)(x & 0xFFFFFFFFu);
            else if (!strcmp(red, "high32")) r = (uint32_t)(x >> 32);
            else if (!strcmp(red, "xor32")) r = (uint32_t)((x ^ (x >> 32)) & 0xFFFFFFFFu);
            else if (!strcmp(red, "lemire1e9p7")) r = (uint32_t)(((unsigned __int128)x * 1000000007u) >> 64);
            else if (!strcmp(red, "mod1e9p7")) r = (uint32_t)(x % 1000000007u);
            else r = (uint32_t)(x % 1000u);
            for (int b = 0; b < wpb && emitted + bi < nbytes; b++)
                buf[bi++] = (uint8_t)(r >> (8 * b));
        }
        if (fwrite(buf, 1, (size_t)bi, stdout) != (size_t)bi) { perror("fwrite"); return 1; }
        emitted += bi;
        done += m;
    }
    fflush(stdout);
    return 0;
}
