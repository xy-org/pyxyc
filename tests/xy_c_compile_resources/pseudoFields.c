#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct pseudoFields_Point pseudoFields_Point;
typedef struct pseudoFields_CoordField pseudoFields_CoordField;

struct pseudoFields_CoordField {
    uint32_t m_i;
};
struct pseudoFields_Point {
    float m_coords[3];
};

float pseudoFields_get(pseudoFields_Point p, pseudoFields_CoordField f) {
    return p.m_coords[f.m_i];
}

void pseudoFields_set(pseudoFields_Point* p, pseudoFields_CoordField f, float val) {
    return p->m_coords[f.m_i] = val;
}

void pseudoFields_test(void) {
    pseudoFields_Point p1 = (pseudoFields_Point){0};
    pseudoFields_set(&p1, (pseudoFields_CoordField){0}, 10.0f);
    pseudoFields_set(&p1, (pseudoFields_CoordField){1}, 20.0f);
    pseudoFields_set(&p1, (pseudoFields_CoordField){2}, pseudoFields_get(p1, (pseudoFields_CoordField){0}) + pseudoFields_get(p1, (pseudoFields_CoordField){1}));
    pseudoFields_set(&p1, (pseudoFields_CoordField){0}, pseudoFields_get(p1, (pseudoFields_CoordField){0}));
    pseudoFields_set(&p1, (pseudoFields_CoordField){0}, p1.m_coords[0]);
    const pseudoFields_Point p2 = (pseudoFields_Point){{10.0f, 20.0f, 30.0f}};
    pseudoFields_Point tmp0 = p1;
    pseudoFields_set(&tmp0, (pseudoFields_CoordField){0}, 10.0f);
    pseudoFields_set(&tmp0, (pseudoFields_CoordField){1}, 20.0f);
    pseudoFields_set(&tmp0, (pseudoFields_CoordField){2}, 30.0f);
    const pseudoFields_Point p3 = tmp0;
    pseudoFields_Point tmp1 = p3;
    pseudoFields_set(&tmp1, (pseudoFields_CoordField){0}, pseudoFields_get(p1, (pseudoFields_CoordField){0}) + pseudoFields_get(p3, (pseudoFields_CoordField){2}));
    pseudoFields_set(&tmp1, (pseudoFields_CoordField){1}, pseudoFields_get(p2, (pseudoFields_CoordField){2}) + pseudoFields_get(p3, (pseudoFields_CoordField){0}));
    pseudoFields_set(&tmp1, (pseudoFields_CoordField){2}, 0.0f);
    const pseudoFields_Point p4 = tmp1;
    pseudoFields_Point tmp2 = p3;
    pseudoFields_set(&tmp2, (pseudoFields_CoordField){2}, pseudoFields_get(p1, (pseudoFields_CoordField){0}));
    pseudoFields_set(&tmp2, (pseudoFields_CoordField){1}, pseudoFields_get(p2, (pseudoFields_CoordField){1}));
    pseudoFields_set(&tmp2, (pseudoFields_CoordField){0}, 0.0f);
    const pseudoFields_Point p5 = tmp2;
    pseudoFields_Point tmp3 = (pseudoFields_Point){0};
    pseudoFields_set(&tmp3, (pseudoFields_CoordField){0}, 0.0f);
    pseudoFields_set(&tmp3, (pseudoFields_CoordField){1}, 1.0f);
    pseudoFields_set(&tmp3, (pseudoFields_CoordField){2}, 2.0f);
    const pseudoFields_Point p6 = tmp3;
    pseudoFields_Point tmp4 = (pseudoFields_Point){0};
    pseudoFields_set(&tmp4, (pseudoFields_CoordField){0}, 0.0f);
    pseudoFields_set(&tmp4, (pseudoFields_CoordField){1}, 1.0f);
    pseudoFields_set(&tmp4, (pseudoFields_CoordField){2}, 2.0f);
    const pseudoFields_Point p7 = tmp4;
    pseudoFields_Point tmp5 = (pseudoFields_Point){{.0f, .0f, .0f}};
    pseudoFields_set(&tmp5, (pseudoFields_CoordField){0}, 10.0f);
    const pseudoFields_Point p8 = tmp5;
    pseudoFields_Point tmp6 = (pseudoFields_Point){0};
    pseudoFields_set(&tmp6, (pseudoFields_CoordField){0}, 10.0f);
    float tmp7[3] = {.1f, .1f, .1f};
    memcpy(&tmp6.m_coords, &tmp7, 3 * sizeof(float));
    const pseudoFields_Point p9 = tmp6;
}
