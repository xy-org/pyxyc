#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void moveOperators3_func1(int32_t* p_a, int32_t p_b) {
}

void moveOperators3_func2(int32_t p_a, int32_t* p_b) {
}

void moveOperators3_test(void) {
    int32_t l_a = 0;
    int32_t tmp_0_arg = l_a;
    l_a = 0;
    moveOperators3_func1(&l_a, tmp_0_arg);
    int32_t tmp_1_arg = l_a;
    l_a = 0;
    moveOperators3_func2(l_a, &tmp_1_arg);
}

void moveOperators3_arrFunc1(int32_t* p_a, int32_t* p_b) {
}

void moveOperators3_arrFunc2(int32_t* p_a, int32_t* p_b) {
}

void moveOperators3_arrTest(void) {
    int32_t l_arr[10] = {0};
    int32_t tmp_0_arg[10] = {l_arr[0], l_arr[1], l_arr[2], l_arr[3], l_arr[4], l_arr[5], l_arr[6], l_arr[7], l_arr[8], l_arr[9]};
    for (size_t tmp_1_i = 0; tmp_1_i < 10; ++tmp_1_i) {
        l_arr[tmp_1_i] = 0;
    }
    moveOperators3_arrFunc1(l_arr, tmp_0_arg);
    int32_t tmp_2_arg[10] = {l_arr[0], l_arr[1], l_arr[2], l_arr[3], l_arr[4], l_arr[5], l_arr[6], l_arr[7], l_arr[8], l_arr[9]};
    for (size_t tmp_3_i = 0; tmp_3_i < 10; ++tmp_3_i) {
        l_arr[tmp_3_i] = 0;
    }
    moveOperators3_arrFunc2(l_arr, tmp_2_arg);
}
