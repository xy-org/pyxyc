#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t arrays_constructingArrays(void) {
    const int32_t l_arr[3] = {0, 1, 2};
    const int32_t l_brr[3] = {3, 4, 5};
    const int32_t l_crr[3] = {6, 7, 8};
    int32_t l_drr[3] = {0};
    const int32_t l_err[4] = {1, 2, 3};
    const int32_t l_frr[3] = {1, 2, 3};
    return l_arr[0] + l_brr[1] + l_crr[2] + l_drr[0] + l_err[1] + l_frr[2];
}
