#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void lambdas2_inner__1(int32_t p_x) {
}

void lambdas2_inner__2(int64_t p_x) {
}

void lambdas2_inner_func_0(int32_t p_x) {
}

void lambdas2_test1(int32_t p_x) {
    lambdas2_inner__1(10);
    lambdas2_inner_func_0(20);
    lambdas2_inner__2(20ll);
    lambdas2_inner_func_0(20);
    lambdas2_inner_func_0(p_x);
}

void lambdas2_test2(int32_t p_x) {
    lambdas2_inner__1(p_x);
}
