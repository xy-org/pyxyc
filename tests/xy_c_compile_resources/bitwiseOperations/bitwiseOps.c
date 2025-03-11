#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

bool bitwiseOps_get(uint64_t b, int32_t i) {
    return (b & (uint64_t)1 << i) != 0;
}

int32_t bitwiseOps_set(uint64_t* b, int32_t i, bool val) {
    *b = *b | (uint64_t)val << i;
    return i;
}

uint64_t bitwiseOps_testBitGetSet(int32_t i) {
    uint64_t b = 0;
    bitwiseOps_set(&b, 0, true);
    bool tmp_arg0 = bitwiseOps_get(b, i);
    bitwiseOps_set(&b, 1, tmp_arg0);
    bool tmp_arg1 = bitwiseOps_get(b, 0);
    bool tmp_arg2 = tmp_arg1 || bitwiseOps_get(b, 12);
    bitwiseOps_set(&b, 10, tmp_arg2);
    return b;
}

void bitwiseOps_testMixing(void) {
    int64_t a = 766624694ll;
    int64_t b = 38098ll;
}
