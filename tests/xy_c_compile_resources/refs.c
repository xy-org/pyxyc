#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct refs_Point refs_Point;

struct refs_Point {
    float m_x;
    float m_y;
    float m_z;
    float m_w;
};

int32_t refs_select(refs_Point p, int32_t idx) {
    return idx;
}

float refs_get(refs_Point p, int32_t idx) {
    return (float[4]){p.m_x, p.m_y, p.m_z, p.m_w}[idx];
}

void refs_set(refs_Point* p, int32_t idx, float v) {
    if (idx == 0) {
        p->m_x = v;
    } else if (idx == 1) {
        p->m_y = v;
    } else if (idx == 2) {
        p->m_z = v;
    } else {
        p->m_w = v;
    }
}

float refs_testPoint(int32_t i) {
    refs_Point p1 = (refs_Point){0, 0, 0, (float)i};
    refs_Point p2 = (refs_Point){0, 0, 0, 1.0f};
    p1.m_x = refs_get(p1, refs_select(p1, i));
    p2.m_z = refs_get(p1, refs_select(p1, 4 - i));
    const float sum = p1.m_x + refs_get(p2, refs_select(p2, 2)) + p2.m_z + refs_get(p1, refs_select(p1, 3));
    float res = refs_get(p1, refs_select(p1, 0));
    int32_t tmp_arg0 = refs_select(p2, 0);
    float tmp_arg1 = refs_get(p1, refs_select(p1, 0));
    if (!(tmp_arg0 <= 3)) {
        abort();
    }
    refs_set(&p2, tmp_arg0, tmp_arg1);
    res += refs_get(p2, refs_select(p2, 0));
    return res + sum;
}
