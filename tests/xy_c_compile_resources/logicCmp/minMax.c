#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t minMax_test__Int__Int(int32_t p_a, int32_t p_b) {
    int32_t tmp_0_arg = p_a + (p_a > p_b ? p_a : p_b) * 2;
    return tmp_0_arg + (p_a < p_b ? p_a : p_b) * 3;
}

uint64_t minMax_test__Ulong__Ulong(uint64_t p_a, uint64_t p_b) {
    uint64_t tmp_0_arg = p_a > p_b ? p_a : p_b;
    uint64_t tmp_1_arg = p_a < p_b ? p_a : p_b;
    return p_a + tmp_0_arg * 2 + tmp_1_arg * 3;
}
