#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t ifs4_test1(int32_t p_a, int32_t p_b) {
    return p_a - p_b;
}

int32_t ifs4_test2(int32_t p_a, int32_t p_b) {
    return p_a + p_b;
    return p_a - p_b;
}

int32_t ifs4_test3(int32_t p_a, int32_t p_b) {
    int32_t l_c = 0;
    if (p_a > p_b) {
        l_c = p_a;
    } else {
        l_c = p_b;
    }
    return l_c;
}
