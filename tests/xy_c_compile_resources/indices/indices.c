#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct indices_Point indices_Point;
typedef struct indices_PointCloud indices_PointCloud;

struct indices_Point {
    float m_x;
    float m_y;
    float m_z;
    float m_w;
};
struct indices_PointCloud {
    void* m_mem;
    size_t m_len;
};

int32_t indices_select__Point__Int(indices_Point p, int32_t idx) {
    return idx;
}

float indices_get__Point__Int(indices_Point p, int32_t idx) {
    float tmp_arg0[4] = {p.m_x, p.m_y, p.m_z, p.m_w};
    return tmp_arg0[idx];
}

void indices_set__Point__Int__Float(indices_Point* p, int32_t idx, float v) {
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

float indices_testPoint(int32_t i) {
    indices_Point p1 = (indices_Point){0, 0, 0, (float)i};
    indices_Point p2 = (indices_Point){0, 0, 0, 1.0f};
    p1.m_x = indices_get__Point__Int(p1, i);
    p2.m_z = indices_get__Point__Int(p1, 4 - i);
    const float sum = p1.m_x + indices_get__Point__Int(p2, 2) + p2.m_z + indices_get__Point__Int(p1, 3);
    float res = indices_get__Point__Int(p1, 0);
    float tmp_arg0 = indices_get__Point__Int(p1, 0);
    if (!(0 <= 3)) {
        abort();
    }
    indices_set__Point__Int__Float(&p2, 0, tmp_arg0);
    res += indices_get__Point__Int(p2, 0);
    return res + sum;
}

void indices_append(indices_PointCloud* pc, indices_Point p) {
    pc->m_len++;
}

int32_t indices_select__PointCloud__Int(indices_PointCloud pc, int32_t i) {
    return i;
}

indices_Point* indices_get__PointCloud__Int(indices_PointCloud pc, int32_t i) {
    return (int8_t*)pc.m_mem + i * sizeof(indices_Point);
}

void indices_set__PointCloud__Int__Point(indices_PointCloud* pc, int32_t i, indices_Point p) {
}

void indices_testPointCloud(indices_PointCloud* m0, indices_PointCloud m1) {
    indices_PointCloud ms = (indices_PointCloud){0};
    indices_append(&ms, (indices_Point){1.0f, 1.0f, .05f, 1.0f});
    indices_append(&ms, (indices_Point){1.0f, 1.0f, .05f, 1.0f});
    const indices_Point p = *indices_get__PointCloud__Int(*m0, 10);
    indices_set__PointCloud__Int__Point(m0, 0, (indices_Point){1.0f, 2.0f, 3.0f, 0.0f});
    indices_get__PointCloud__Int(*m0, 0)->m_y = 10;
    indices_Point* tmp_ref0 = indices_get__PointCloud__Int(m1, 1);
    const float tmp = indices_get__Point__Int(*tmp_ref0, 2);
    indices_set__PointCloud__Int__Point(&ms, 2, *indices_get__PointCloud__Int(*m0, 2));
    indices_get__PointCloud__Int(ms, 2)->m_x = indices_get__PointCloud__Int(*m0, 0)->m_y;
    indices_get__PointCloud__Int(ms, 4)->m_x = 5;
    indices_get__PointCloud__Int(ms, 4)->m_y = 10;
}
