#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void arrayComprehension_func(int32_t* arr) {
}

void arrayComprehension_test(void) {
    const int32_t arr1[3] = {1, 2, 3};
    const int32_t arr2[3] = {arr1[0] * 2, arr1[1] * 2, arr1[2] * 2};
    int32_t tmp_arg0[3] = {3, 2, 1};
    const int32_t arr3[3] = {tmp_arg0[0], tmp_arg0[1], tmp_arg0[2]};
    arrayComprehension_func(arr2);
    int32_t tmp_arg1[3] = {3, 2, 1};
    int32_t tmp_arg2[3] = {tmp_arg1[0], tmp_arg1[1], tmp_arg1[2]};
    arrayComprehension_func(tmp_arg2);
}
