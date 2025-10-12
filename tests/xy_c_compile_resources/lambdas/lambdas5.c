#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef int32_t (*xy_fp__Int__Int)(int32_t) ;

int32_t lambdas5_inner_func_0(int32_t p_base, int32_t p_x) {
    return p_base + p_x;
}

int32_t xy_gen__lambdas5__cb1(int32_t p_param0) {
    return lambdas5_inner_func_0(p_param0, 10);
}

int32_t lambdas5_inner_func_2(int32_t p_base, int32_t p_x) {
    return p_base + p_x;
}

int32_t xy_gen__lambdas5__cb3(int32_t p_param0) {
    return lambdas5_inner_func_2(p_param0, 20);
}

int32_t lambdas5_test(void) {
    const xy_fp__Int__Int l_cb1 = xy_gen__lambdas5__cb1;
    const xy_fp__Int__Int l_cb2 = xy_gen__lambdas5__cb3;
    int32_t tmp_0_arg = l_cb1(30);
    return tmp_0_arg + l_cb2(0);
}
