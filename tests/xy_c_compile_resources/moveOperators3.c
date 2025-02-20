#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void moveOperators3_func1(int32_t* a, int32_t b) {
}

void moveOperators3_func2(int32_t a, int32_t* b) {
}

void moveOperators3_test(void) {
    int32_t a = 0;
    int32_t tmp_arg0 = a;
    a = 0;
    moveOperators3_func1(&a, tmp_arg0);
    int32_t tmp_arg1 = a;
    a = 0;
    moveOperators3_func2(a, &tmp_arg1);
}

void moveOperators3_arrFunc1(int32_t* a, int32_t* b) {
}

void moveOperators3_arrFunc2(int32_t* a, int32_t* b) {
}

void moveOperators3_arrTest(void) {
    int32_t arr[10] = {0};
    int32_t tmp_arg0[10] = {arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], arr[6], arr[7], arr[8], arr[9]};
    for (size_t tmp_i1 = 0; tmp_i1 < 10; ++tmp_i1) {
        arr[tmp_i1] = 0;
    }
    moveOperators3_arrFunc1(arr, tmp_arg0);
    int32_t tmp_arg2[10] = {arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], arr[6], arr[7], arr[8], arr[9]};
    for (size_t tmp_i3 = 0; tmp_i3 < 10; ++tmp_i3) {
        arr[tmp_i3] = 0;
    }
    moveOperators3_arrFunc2(arr, tmp_arg2);
}
