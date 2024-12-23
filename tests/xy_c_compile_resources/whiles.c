#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t whiles_func1(int32_t x, int32_t y) {
    int32_t i = 0;
    while (x < y) {
        x += 10;
        i++;
    }
    return i;
}

int32_t whiles_func2(int32_t x, int32_t y) {
    int32_t __tmp_i0;
    while (x < y) {
        x += 10;
        __tmp_i0++;
    }
    return __tmp_i0;
}

int32_t whiles_func3(int32_t x, int32_t y) {
    int32_t i = 0;
    while (x < y) {
        x += 10;
        i++;
        if (i > 10) {
            break;
        }
    }
    return i;
}
