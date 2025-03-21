#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void moveOperators3_func1(int32_t* p_a, int32_t p_b) {
}

void moveOperators3_func2(int32_t p_a, int32_t* p_b) {
}

void moveOperators3_test(void) {
    int32_t l_a = 0;
    int32_t tmp_arg0 = l_a;
    l_a = 0;
    moveOperators3_func1(&l_a, tmp_arg0);
    int32_t tmp_arg1 = l_a;
    l_a = 0;
    moveOperators3_func2(l_a, &tmp_arg1);
}

void moveOperators3_arrFunc1(int32_t* p_a, int32_t* p_b) {
}

void moveOperators3_arrFunc2(int32_t* p_a, int32_t* p_b) {
}

void moveOperators3_arrTest(void) {
    int32_t l_arr[10] = {0};
    int32_t tmp_arg0[10] = {l_arr[0], l_arr[1], l_arr[2], l_arr[3], l_arr[4], l_arr[5], l_arr[6], l_arr[7], l_arr[8], l_arr[9]};
    for (size_t tmp_i1 = 0; tmp_i1 < 10; ++tmp_i1) {
        l_arr[tmp_i1] = 0;
    }
    moveOperators3_arrFunc1(l_arr, tmp_arg0);
    int32_t tmp_arg2[10] = {l_arr[0], l_arr[1], l_arr[2], l_arr[3], l_arr[4], l_arr[5], l_arr[6], l_arr[7], l_arr[8], l_arr[9]};
    for (size_t tmp_i3 = 0; tmp_i3 < 10; ++tmp_i3) {
        l_arr[tmp_i3] = 0;
    }
    moveOperators3_arrFunc2(l_arr, tmp_arg2);
}
