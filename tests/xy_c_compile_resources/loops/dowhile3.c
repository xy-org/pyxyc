#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct dowhile3_TypeWithDtor dowhile3_TypeWithDtor;

struct dowhile3_TypeWithDtor {
    int32_t m_id;
};

bool dowhile3_cond1(int32_t p_a, int32_t p_b) {
    return p_a >= p_b * 2;
}

bool dowhile3_cond2(int32_t p_a, int32_t p_b) {
    return p_b < 10;
}

void dowhile3_dtor(dowhile3_TypeWithDtor p_resource) {
}

void dowhile3_test(int32_t* p_x, int32_t* p_y) {
    do {
        const dowhile3_TypeWithDtor l_a = {-1};
        (*p_x)--;
        do {
            const dowhile3_TypeWithDtor l_b = {-2};
            (*p_y)++;
            if (*p_y > 0) {
                dowhile3_dtor(l_b);
                dowhile3_dtor(l_a);
                continue;
            } else if (*p_y < -500) {
                dowhile3_dtor(l_b);
                break;
            }
            dowhile3_dtor(l_b);
            if (!(*p_y < *p_x)) {
                abort();
            }
        } while (dowhile3_cond2(*p_y, *p_x));
        (*p_y)--;
        dowhile3_dtor(l_a);
        if (!(*p_x >= *p_y)) {
            abort();
        }
    } while (dowhile3_cond1(*p_x, *p_y));
}
