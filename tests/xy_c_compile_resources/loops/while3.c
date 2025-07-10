#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct while3_TypeWithDtor while3_TypeWithDtor;

struct while3_TypeWithDtor {
    int32_t m_id;
};

bool while3_cond1(int32_t p_a, int32_t p_b) {
    return true;
}

bool while3_cond2(int32_t p_a, int32_t p_b) {
    return p_b < 10;
}

void while3_dtor(while3_TypeWithDtor p_resource) {
}

void while3_test(int32_t* p_x, int32_t* p_y) {
    if (!(*p_x >= *p_y)) {
        abort();
    }
    bool tmp_0_arg = while3_cond1(*p_x, *p_y);
    bool tmp_2_shortcircuit = tmp_0_arg;
    if (tmp_2_shortcircuit) {
        if (!(*p_y < *p_x)) {
            abort();
        }
        tmp_2_shortcircuit = while3_cond2(*p_y, *p_x);
    }
    while (tmp_2_shortcircuit) {
        (*p_x)--;
        while3_TypeWithDtor l_a = {-1};
        if (*p_x == 10) {
            while3_TypeWithDtor l_b = {-1};
            if (*p_y < 20) {
                while3_dtor(l_b);
                while3_dtor(l_a);
                goto L_0_CONTINUE_;
            }
            while3_dtor(l_b);
        }
        (*p_y)++;
        while3_dtor(l_a);
    L_0_CONTINUE_:
        if (!(*p_x >= *p_y)) {
            abort();
        }
        bool tmp_3_arg = while3_cond1(*p_x, *p_y);
        bool tmp_5_shortcircuit = tmp_3_arg;
        if (tmp_5_shortcircuit) {
            if (!(*p_y < *p_x)) {
                abort();
            }
            tmp_5_shortcircuit = while3_cond2(*p_y, *p_x);
        }
        tmp_2_shortcircuit = tmp_5_shortcircuit;
    }
}
