#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef int32_t (*xy_fp__Ptr__Int)(void*) ;

void lambdas6_f2(xy_fp__Ptr__Int p_cb) {
    int32_t l_num = 10;
    const int32_t l_res = p_cb(&l_num);
}

int64_t lambdas6_my(int32_t p_x) {
    return (int64_t)p_x;
}

int32_t xy_gen__lambdas6__cb1(void* p_param0) {
    return (int32_t)lambdas6_my(*(int32_t*)p_param0);
}

int32_t lambdas6_something_func_2(int32_t p_x) {
    return 500;
}

int32_t xy_gen__lambdas6__cb4(void* p_param0) {
    return (int32_t)lambdas6_something_func_2(*(int32_t*)p_param0);
}

void lambdas6_test(void) {
    lambdas6_f2(xy_gen__lambdas6__cb1);
    lambdas6_f2(xy_gen__lambdas6__cb4);
}
