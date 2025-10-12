#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t lambdas3_inner_func_0(int32_t p_base) {
    return p_base;
}

int32_t lambdas3_inner_func_1(int32_t p_base) {
    return p_base;
}

int32_t lambdas3_test(void) {
    const int32_t l_a = lambdas3_inner_func_0(20);
    const int32_t l_b = lambdas3_inner_func_1(30);
    return l_a + l_b;
}
