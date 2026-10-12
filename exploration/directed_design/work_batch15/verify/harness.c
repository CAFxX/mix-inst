
#include <stdint.h>
#include <stdio.h>
uint64_t mix_hash(uint64_t v, uint64_t k);
int main(void) {
    unsigned long long v, k;
    while (scanf("%llx %llx", &v, &k) == 2)
        printf("%016llx\n", (unsigned long long)mix_hash((uint64_t)v, (uint64_t)k));
    return 0;
}
