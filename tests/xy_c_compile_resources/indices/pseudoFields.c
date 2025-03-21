#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

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
    float tmp_arg0 = pseudoFields_get(l_p1, (pseudoFields_CoordField){0});
    pseudoFields_set(&l_p1, (pseudoFields_CoordField){2}, tmp_arg0 + pseudoFields_get(l_p1, (pseudoFields_CoordField){1}));
    pseudoFields_set(&l_p1, (pseudoFields_CoordField){0}, pseudoFields_get(l_p1, (pseudoFields_CoordField){0}));
    pseudoFields_set(&l_p1, (pseudoFields_CoordField){0}, l_p1.m_coords[0]);
    const pseudoFields_Point l_p2 = {{10.0f, 20.0f, 30.0f}};
    pseudoFields_Point tmp1 = l_p1;
    pseudoFields_set(&tmp1, (pseudoFields_CoordField){0}, 10.0f);
    pseudoFields_set(&tmp1, (pseudoFields_CoordField){1}, 20.0f);
    pseudoFields_set(&tmp1, (pseudoFields_CoordField){2}, 30.0f);
    const pseudoFields_Point l_p3 = tmp1;
    pseudoFields_Point tmp2 = l_p3;
    float tmp_arg3 = pseudoFields_get(l_p1, (pseudoFields_CoordField){0});
    float tmp_arg4 = pseudoFields_get(l_p2, (pseudoFields_CoordField){2});
    pseudoFields_set(&tmp2, (pseudoFields_CoordField){0}, tmp_arg3 + pseudoFields_get(l_p3, (pseudoFields_CoordField){2}));
    pseudoFields_set(&tmp2, (pseudoFields_CoordField){1}, tmp_arg4 + pseudoFields_get(l_p3, (pseudoFields_CoordField){0}));
    pseudoFields_set(&tmp2, (pseudoFields_CoordField){2}, 0.0f);
    const pseudoFields_Point l_p4 = tmp2;
    pseudoFields_Point tmp5 = l_p3;
    pseudoFields_set(&tmp5, (pseudoFields_CoordField){2}, pseudoFields_get(l_p1, (pseudoFields_CoordField){0}));
    pseudoFields_set(&tmp5, (pseudoFields_CoordField){1}, pseudoFields_get(l_p2, (pseudoFields_CoordField){1}));
    pseudoFields_set(&tmp5, (pseudoFields_CoordField){0}, 0.0f);
    const pseudoFields_Point l_p5 = tmp5;
    pseudoFields_Point tmp6 = (pseudoFields_Point){0};
    pseudoFields_set(&tmp6, (pseudoFields_CoordField){0}, 0.0f);
    pseudoFields_set(&tmp6, (pseudoFields_CoordField){1}, 1.0f);
    pseudoFields_set(&tmp6, (pseudoFields_CoordField){2}, 2.0f);
    const pseudoFields_Point l_p6 = tmp6;
    pseudoFields_Point tmp7 = (pseudoFields_Point){0};
    pseudoFields_set(&tmp7, (pseudoFields_CoordField){0}, 0.0f);
    pseudoFields_set(&tmp7, (pseudoFields_CoordField){1}, 1.0f);
    pseudoFields_set(&tmp7, (pseudoFields_CoordField){2}, 2.0f);
    const pseudoFields_Point l_p7 = tmp7;
    pseudoFields_Point tmp8 = (pseudoFields_Point){{.0f, .0f, .0f}};
    pseudoFields_set(&tmp8, (pseudoFields_CoordField){0}, 10.0f);
    const pseudoFields_Point l_p8 = tmp8;
    pseudoFields_Point tmp9 = (pseudoFields_Point){0};
    pseudoFields_set(&tmp9, (pseudoFields_CoordField){0}, 10.0f);
    float tmp10[3] = {.1f, .1f, .1f};
    memcpy(&tmp9.m_coords, &tmp10, 3 * sizeof(float));
    const pseudoFields_Point l_p9 = tmp9;
}
