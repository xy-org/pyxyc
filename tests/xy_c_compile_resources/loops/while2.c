#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

bool while2_cond1(int32_t p_a, int32_t p_b) {
    return true;
}

bool while2_cond2(int32_t p_b) {
    return p_b < 10;
}

void while2_test(int32_t* p_x, int32_t* p_y) {
    if (!(*p_x >= *p_y)) {
        abort();
    }
    bool tmp_2_arg = while2_cond1(*p_x, *p_y);
    bool tmp_6_shortcircuit = tmp_2_arg;
    if (tmp_6_shortcircuit) {
        if (!(*p_x >= *p_y)) {
            abort();
        }
        bool tmp_5_arg = while2_cond1(*p_x, *p_y);
        if (!((int32_t)tmp_5_arg < *p_x)) {
            abort();
        }
        tmp_6_shortcircuit = while2_cond2(*p_x);
    }
    while (tmp_6_shortcircuit) {
        (*p_x)--;
        (*p_y)++;
        if (!(*p_x >= *p_y)) {
            abort();
        }
        bool tmp_9_arg = while2_cond1(*p_x, *p_y);
        bool tmp_13_shortcircuit = tmp_9_arg;
        if (tmp_13_shortcircuit) {
            if (!(*p_x >= *p_y)) {
                abort();
            }
            bool tmp_12_arg = while2_cond1(*p_x, *p_y);
            if (!((int32_t)tmp_12_arg < *p_x)) {
                abort();
            }
            tmp_13_shortcircuit = while2_cond2(*p_x);
        }
        tmp_6_shortcircuit = tmp_13_shortcircuit;
    }
}
