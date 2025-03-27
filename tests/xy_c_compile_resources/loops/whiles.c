#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t whiles_func1(int32_t p_x, int32_t p_y) {
    int32_t l_i = 0;
    while (p_x < p_y) {
        p_x += 10;
        l_i++;
    }
    return l_i;
}

int32_t whiles_func2(int32_t p_x, int32_t p_y) {
    int32_t tmp_0_i = 0;
    while (p_x < p_y) {
        p_x += 10;
        tmp_0_i++;
    }
    return tmp_0_i;
}

int32_t whiles_func3(int32_t p_x, int32_t p_y) {
    int32_t l_i = 0;
    while (p_x < p_y) {
        p_x += 10;
        l_i++;
        if (l_i > 10) {
            break;
        }
    }
    return l_i;
}

bool whiles_cond(void) {
    return true;
}

int32_t whiles_update(void) {
    return 1;
}

int32_t whiles_func4(int32_t p_x, int32_t p_y) {
    int32_t tmp_0_res = 0;
    while (whiles_cond()) {
        tmp_0_res += whiles_update();
    }
    return tmp_0_res;
}
