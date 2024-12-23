#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct refs_Point refs_Point;
typedef struct refs_PointCloud refs_PointCloud;

struct refs_Point {
    float m_x;
    float m_y;
    float m_z;
    float m_w;
};
struct refs_PointCloud {
    void* m_mem;
    size_t m_len;
};

int32_t refs_select__Point__int(refs_Point p, int32_t idx) {
    return idx;
}

float refs_get__Point__int(refs_Point p, int32_t idx) {
    return (float[4]){p.m_x, p.m_y, p.m_z, p.m_w}[idx];
}

void refs_set__Point__int__float(refs_Point* p, int32_t idx, float v) {
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
    p1.m_x = refs_get__Point__int(p1, refs_select__Point__int(p1, i));
    p2.m_z = refs_get__Point__int(p1, refs_select__Point__int(p1, 4 - i));
    const float sum = p1.m_x + refs_get__Point__int(p2, refs_select__Point__int(p2, 2)) + p2.m_z + refs_get__Point__int(p1, refs_select__Point__int(p1, 3));
    float res = refs_get__Point__int(p1, refs_select__Point__int(p1, 0));
    int32_t tmp_arg0 = refs_select__Point__int(p2, 0);
    float tmp_arg1 = refs_get__Point__int(p1, refs_select__Point__int(p1, 0));
    if (!(tmp_arg0 <= 3)) {
        abort();
    }
    refs_set__Point__int__float(&p2, tmp_arg0, tmp_arg1);
    res += refs_get__Point__int(p2, refs_select__Point__int(p2, 0));
    return res + sum;
}

void refs_append(refs_PointCloud* pc, refs_Point p) {
    pc->m_len++;
}

int32_t refs_select__PointCloud__int(refs_PointCloud pc, int32_t i) {
    return i;
}

refs_Point* refs_get__PointCloud__int(refs_PointCloud pc, int32_t i) {
    return (int8_t*)pc.m_mem + i * sizeof(refs_Point);
}

void refs_set__PointCloud__int__Point(refs_PointCloud* pc, int32_t i, refs_Point p) {
}

void refs_testPointCloud(refs_PointCloud* m0, refs_PointCloud m1) {
    refs_PointCloud ms = (refs_PointCloud){0};
    refs_append(&ms, (refs_Point){1.0f, 1.0f, .05f, 1.0f});
    refs_append(&ms, (refs_Point){1.0f, 1.0f, .05f, 1.0f});
    const refs_Point p = *refs_get__PointCloud__int(*m0, refs_select__PointCloud__int(*m0, 10));
    int32_t tmp_arg0 = refs_select__PointCloud__int(*m0, 0);
    refs_set__PointCloud__int__Point(m0, tmp_arg0, (refs_Point){1.0f, 2.0f, 3.0f, 0.0f});
    refs_get__PointCloud__int(*m0, refs_select__PointCloud__int(*m0, 0))->m_y = 10;
    refs_Point tmp_arg1 = *refs_get__PointCloud__int(m1, refs_select__PointCloud__int(m1, 1));
    const float tmp = refs_get__Point__int(tmp_arg1, refs_select__Point__int(tmp_arg1, 2));
    int32_t tmp_arg2 = refs_select__PointCloud__int(ms, 2);
    refs_set__PointCloud__int__Point(&ms, tmp_arg2, *refs_get__PointCloud__int(*m0, refs_select__PointCloud__int(*m0, 2)));
    refs_get__PointCloud__int(ms, refs_select__PointCloud__int(ms, 2))->m_x = refs_get__PointCloud__int(*m0, refs_select__PointCloud__int(*m0, 0))->m_y;
    refs_get__PointCloud__int(ms, refs_select__PointCloud__int(ms, 4))->m_x = 5;
    refs_get__PointCloud__int(ms, refs_select__PointCloud__int(ms, 4))->m_y = 10;
}
