#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef int32_t (*xy_fp__Int__Int__Int)(int32_t, int32_t) ;

int32_t callbacksAcrossModules1_module1_something(xy_fp__Int__Int__Int p_cb) {
    return p_cb(10, 100);
}

int32_t callbacksAcrossModules1_module1_indirectCmp_func_0(int32_t p_a, int32_t p_b) {
    return p_a > p_b ? 1 : p_a == p_b ? 0 : -1;
}

int32_t xy_gen__callbacksAcrossModules1_module1__cb1(int32_t p_param0, int32_t p_param1) {
    return callbacksAcrossModules1_module1_indirectCmp_func_0(p_param0, p_param1);
}

void callbacksAcrossModules1_module1_inModule1(void) {
    const int32_t l_x = callbacksAcrossModules1_module1_something(xy_gen__callbacksAcrossModules1_module1__cb1);
}

int32_t callbacksAcrossModules1_module1_indirectCmp_func_2(int32_t p_a, int32_t p_b) {
    return p_a > p_b ? 1 : p_a == p_b ? 0 : -1;
}

int32_t xy_gen__callbacksAcrossModules1_module1__cb3(int32_t p_param0, int32_t p_param1) {
    return callbacksAcrossModules1_module1_indirectCmp_func_2(p_param0, p_param1);
}

void callbacksAcrossModules1_test(void) {
    const int32_t l_y = callbacksAcrossModules1_module1_something(xy_gen__callbacksAcrossModules1_module1__cb3);
}
