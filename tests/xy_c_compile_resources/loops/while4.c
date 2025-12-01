#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct while4_TypeWithDtor while4_TypeWithDtor;

struct while4_TypeWithDtor {
    int32_t m_id;
};

bool while4_cond1(int32_t p_a, int32_t p_b) {
    return true;
}

bool while4_cond2(int32_t p_a, int32_t p_b) {
    return p_b < 10;
}

void while4_dtor(while4_TypeWithDtor p_resource) {
}

void while4_test(int32_t* p_x, int32_t* p_y) {
    if (!(*p_x >= *p_y)) {
        abort();
    }
    bool tmp_0_arg = while4_cond1(*p_x, *p_y);
    while (tmp_0_arg) {
        while4_TypeWithDtor l_a = {-1};
        (*p_x)--;
        if (!(*p_y < *p_x)) {
            abort();
        }
        bool tmp_1_arg = while4_cond2(*p_y, *p_x);
        while (tmp_1_arg) {
            (*p_y)++;
            if (*p_y > 0) {
                while4_dtor(l_a);
                l_a = (while4_TypeWithDtor){0};
                goto L_0_CONTINUE_;
            }
            if (!(*p_y < *p_x)) {
                abort();
            }
            tmp_1_arg = while4_cond2(*p_y, *p_x);
        }
        (*p_y)--;
        while4_dtor(l_a);
    L_0_CONTINUE_:
        if (!(*p_x >= *p_y)) {
            abort();
        }
        tmp_0_arg = while4_cond1(*p_x, *p_y);
    }
}
