#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct refs_Point refs_Point;

struct refs_Point {
    float m_x;
    float m_y;
    float m_z;
    float m_w;
};

int8_t refs_index(refs_Point p, int8_t idx) {
    return idx;
}

float refs_get(refs_Point p, int8_t idx) {
    return (float[4]){p.m_x, p.m_y, p.m_z, p.m_w}[idx];
}

void refs_set(refs_Point* p, int8_t idx, float v) {
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
