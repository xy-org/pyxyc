#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void arrays_constructingArrays(void) {
    int32_t arr[3] = {0, 1, 2};
    int32_t brr[3] = {3, 4, 5};
    int32_t crr[3] = {6, 7, 8};
    int32_t drr[3] = {};
    return arr[0] + brr[1] + crr[2] + drr[0];
}