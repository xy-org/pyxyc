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
    while (while1_cond(*p_x, *p_y)) {
        (*p_x)--;
        if (!(*p_x >= *p_y)) {
            abort();
        }
    }
}
