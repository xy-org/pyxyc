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
    int32_t tmp_i0 = 0;
    while (x < y) {
        x += 10;
        tmp_i0++;
    }
    return tmp_i0;
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

bool whiles_cond(void) {
    return true;
}

int32_t whiles_update(void) {
    return 1;
}

int32_t whiles_func4(int32_t x, int32_t y) {
    int32_t tmp_res0 = 0;
    while (whiles_cond()) {
        tmp_res0 += whiles_update();
    }
    return tmp_res0;
}
