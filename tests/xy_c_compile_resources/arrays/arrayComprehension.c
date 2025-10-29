#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void arrayComprehension_fun(int32_t* p_arr) {
}

void arrayComprehension_test(void) {
    const int32_t l_arr1[3] = {1, 2, 3};
    const int32_t l_arr2[3] = {l_arr1[0] * 2, l_arr1[1] * 2, l_arr1[2] * 2};
    int32_t tmp_0_arg[3] = {3, 2, 1};
    const int32_t l_arr3[3] = {tmp_0_arg[0], tmp_0_arg[1], tmp_0_arg[2]};
    arrayComprehension_fun(l_arr2);
    int32_t tmp_1_arg[3] = {3, 2, 1};
    int32_t tmp_2_arg[3] = {tmp_1_arg[0], tmp_1_arg[1], tmp_1_arg[2]};
    arrayComprehension_fun(tmp_2_arg);
}
