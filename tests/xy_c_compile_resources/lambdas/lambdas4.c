#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t lambdas4_inner_func_0(int32_t p_base, int32_t p_x) {
    return p_base + p_x;
}

int32_t lambdas4_inner_func_1(int32_t p_base, int32_t p_x) {
    return p_base + p_x;
}

int32_t lambdas4_test(void) {
    const int32_t l_a = lambdas4_inner_func_0(20, 10);
    const int32_t l_b = lambdas4_inner_func_1(30, 20);
    return l_a + l_b;
}
