#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

typedef struct pseudoFields_Point pseudoFields_Point;
typedef struct pseudoFields_CoordField pseudoFields_CoordField;

struct pseudoFields_Point {
    float m_coords[3];
};
struct pseudoFields_CoordField {
    uint32_t m_i;
};

float pseudoFields_get(pseudoFields_Point p_p, pseudoFields_CoordField p_f) {
    return p_p.m_coords[p_f.m_i];
}

void pseudoFields_set(pseudoFields_Point* p_p, pseudoFields_CoordField p_f, float p_val) {
    p_p->m_coords[p_f.m_i] = p_val;
}

void pseudoFields_test(void) {
    pseudoFields_Point l_p1 = {0};
    pseudoFields_set(&l_p1, (pseudoFields_CoordField){0}, 10.0f);
    pseudoFields_set(&l_p1, (pseudoFields_CoordField){1}, 20.0f);
    float tmp_0_arg = pseudoFields_get(l_p1, (pseudoFields_CoordField){0});
    pseudoFields_set(&l_p1, (pseudoFields_CoordField){2}, tmp_0_arg + pseudoFields_get(l_p1, (pseudoFields_CoordField){1}));
    pseudoFields_set(&l_p1, (pseudoFields_CoordField){0}, pseudoFields_get(l_p1, (pseudoFields_CoordField){0}));
    pseudoFields_set(&l_p1, (pseudoFields_CoordField){0}, l_p1.m_coords[0]);
    const pseudoFields_Point l_p2 = {{10.0f, 20.0f, 30.0f}};
    pseudoFields_Point tmp_1 = l_p1;
    pseudoFields_set(&tmp_1, (pseudoFields_CoordField){0}, 10.0f);
    pseudoFields_set(&tmp_1, (pseudoFields_CoordField){1}, 20.0f);
    pseudoFields_set(&tmp_1, (pseudoFields_CoordField){2}, 30.0f);
    const pseudoFields_Point l_p3 = tmp_1;
    pseudoFields_Point tmp_2 = l_p3;
    float tmp_3_arg = pseudoFields_get(l_p1, (pseudoFields_CoordField){0});
    float tmp_4_arg = pseudoFields_get(l_p2, (pseudoFields_CoordField){2});
    pseudoFields_set(&tmp_2, (pseudoFields_CoordField){0}, tmp_3_arg + pseudoFields_get(l_p3, (pseudoFields_CoordField){2}));
    pseudoFields_set(&tmp_2, (pseudoFields_CoordField){1}, tmp_4_arg + pseudoFields_get(l_p3, (pseudoFields_CoordField){0}));
    pseudoFields_set(&tmp_2, (pseudoFields_CoordField){2}, 0.0f);
    const pseudoFields_Point l_p4 = tmp_2;
    pseudoFields_Point tmp_5 = l_p3;
    pseudoFields_set(&tmp_5, (pseudoFields_CoordField){2}, pseudoFields_get(l_p1, (pseudoFields_CoordField){0}));
    pseudoFields_set(&tmp_5, (pseudoFields_CoordField){1}, pseudoFields_get(l_p2, (pseudoFields_CoordField){1}));
    pseudoFields_set(&tmp_5, (pseudoFields_CoordField){0}, 0.0f);
    const pseudoFields_Point l_p5 = tmp_5;
    pseudoFields_Point tmp_6 = (pseudoFields_Point){0};
    pseudoFields_set(&tmp_6, (pseudoFields_CoordField){0}, 0.0f);
    pseudoFields_set(&tmp_6, (pseudoFields_CoordField){1}, 1.0f);
    pseudoFields_set(&tmp_6, (pseudoFields_CoordField){2}, 2.0f);
    const pseudoFields_Point l_p6 = tmp_6;
    pseudoFields_Point tmp_7 = (pseudoFields_Point){0};
    pseudoFields_set(&tmp_7, (pseudoFields_CoordField){0}, 0.0f);
    pseudoFields_set(&tmp_7, (pseudoFields_CoordField){1}, 1.0f);
    pseudoFields_set(&tmp_7, (pseudoFields_CoordField){2}, 2.0f);
    const pseudoFields_Point l_p7 = tmp_7;
    pseudoFields_Point tmp_8 = (pseudoFields_Point){{.0f, .0f, .0f}};
    pseudoFields_set(&tmp_8, (pseudoFields_CoordField){0}, 10.0f);
    const pseudoFields_Point l_p8 = tmp_8;
    pseudoFields_Point tmp_9 = (pseudoFields_Point){0};
    pseudoFields_set(&tmp_9, (pseudoFields_CoordField){0}, 10.0f);
    float tmp_10[3] = {.1f, .1f, .1f};
    memcpy(&tmp_9.m_coords, &tmp_10, 3 * sizeof(float));
    const pseudoFields_Point l_p9 = tmp_9;
}
