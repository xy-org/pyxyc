#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

bool boundaryExpr4_cond1(int32_t p_a, int32_t p_b) {
    return p_a >= p_b * 10;
}

bool boundaryExpr4_cond2(int32_t p_b) {
    return p_b < 10;
}

bool boundaryExpr4_test(int32_t* p_x, int32_t* p_y) {
    if (!(*p_x >= *p_y)) {
        abort();
    }
    bool tmp_2_arg = boundaryExpr4_cond1(*p_x, *p_y);
    bool tmp_6_shortcircuit = tmp_2_arg;
    if (tmp_6_shortcircuit) {
        if (!(*p_x >= *p_y)) {
            abort();
        }
        bool tmp_5_arg = boundaryExpr4_cond1(*p_x, *p_y);
        if (!((int32_t)tmp_5_arg < *p_x)) {
            abort();
        }
        tmp_6_shortcircuit = boundaryExpr4_cond2(*p_x);
    }
    return tmp_6_shortcircuit;
}
