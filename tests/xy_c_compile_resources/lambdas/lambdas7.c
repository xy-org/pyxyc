#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t lambdas7_do1(int32_t p_a);
int32_t lambdas7_do2(int32_t p_a);

int32_t lambdas7_do1(int32_t p_a) {
    return p_a + 1;
}

int32_t lambdas7_do2(int32_t p_a) {
    return p_a * 2;
}

bool lambdas7_cond(int32_t p_a, int32_t p_b, int32_t p_c) {
    return p_b + p_a > p_c;
}

void lambdas7_noop_func_0(void) {
}

void lambdas7_test(int32_t p_a) {
    int32_t tmp_0_arg = lambdas7_do1(p_a + 10);
    const bool l_x = lambdas7_cond(p_a + 10, tmp_0_arg, lambdas7_do2(tmp_0_arg));
    int32_t tmp_1_arg = lambdas7_do1(p_a + 10);
    const bool l_y = lambdas7_cond(p_a + 10, tmp_1_arg, lambdas7_do2(tmp_1_arg));
}
