
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
uint64_t mix_hash(uint64_t v, uint64_t k);
int main() {
    uint64_t v, k;
    while (scanf("%" SCNx64 " %" SCNx64, &v, &k) == 2)
        printf("%016" PRIx64 "\n", mix_hash(v, k));
    return 0;
}
