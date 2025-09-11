#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct moveOperators6_Point moveOperators6_Point;

struct moveOperators6_Point {
    int32_t m_x;
    int32_t m_y;
};

void moveOperators6_dtor(moveOperators6_Point p_p) {
}

void moveOperators6_test(moveOperators6_Point* p_a, moveOperators6_Point* p_b) {
    moveOperators6_Point tmp_0_arg = *p_b;
    *p_b = (moveOperators6_Point){1, 2};
    moveOperators6_dtor(*p_a);
    *p_a = tmp_0_arg;
    moveOperators6_dtor(*p_b);
    *p_b = (moveOperators6_Point){1, 2};
    *p_a = (moveOperators6_Point){1, 2};
}
