#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

bool while1_cond(int32_t p_a, int32_t p_b) {
    return p_a > 0;
}

void while1_test(int32_t* p_x, int32_t* p_y) {
    if (!(*p_x >= *p_y)) {
        abort();
    }
    bool tmp_0_arg = while1_cond(*p_x, *p_y);
    while (tmp_0_arg) {
        (*p_x)--;
        if (!(*p_x >= *p_y)) {
            abort();
        }
        tmp_0_arg = while1_cond(*p_x, *p_y);
    }
}
