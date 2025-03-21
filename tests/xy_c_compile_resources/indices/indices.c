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

int32_t indices_select__Point__Int(indices_Point p_p, int32_t p_idx) {
    return p_idx;
}

float indices_get__Point__Int(indices_Point p_p, int32_t p_idx) {
    float tmp_arg0[4] = {p_p.m_x, p_p.m_y, p_p.m_z, p_p.m_w};
    return tmp_arg0[p_idx];
}

void indices_set__Point__Int__Float(indices_Point* p_p, int32_t p_idx, float p_v) {
    if (p_idx == 0) {
        p_p->m_x = p_v;
    } else if (p_idx == 1) {
        p_p->m_y = p_v;
    } else if (p_idx == 2) {
        p_p->m_z = p_v;
    } else {
        p_p->m_w = p_v;
    }
}

float indices_testPoint(int32_t p_i) {
    indices_Point l_p1 = {0, 0, 0, (float)p_i};
    indices_Point l_p2 = {0, 0, 0, 1.0f};
    l_p1.m_x = indices_get__Point__Int(l_p1, p_i);
    l_p2.m_z = indices_get__Point__Int(l_p1, 4 - p_i);
    float tmp_arg0 = l_p1.m_x + indices_get__Point__Int(l_p2, 2) + l_p2.m_z;
    const float l_sum = tmp_arg0 + indices_get__Point__Int(l_p1, 3);
    float l_res = indices_get__Point__Int(l_p1, 0);
    float tmp_arg1 = indices_get__Point__Int(l_p1, 0);
    if (!(0 <= 3)) {
        abort();
    }
    indices_set__Point__Int__Float(&l_p2, 0, tmp_arg1);
    l_res += indices_get__Point__Int(l_p2, 0);
    return l_res + l_sum;
}

void indices_append(indices_PointCloud* p_pc, indices_Point p_p) {
    p_pc->m_len++;
}

int32_t indices_select__PointCloud__Int(indices_PointCloud p_pc, int32_t p_i) {
    return p_i;
}

indices_Point* indices_get__PointCloud__Int(indices_PointCloud p_pc, int32_t p_i) {
    return (int8_t*)p_pc.m_mem + p_i * sizeof(indices_Point);
}

void indices_set__PointCloud__Int__Point(indices_PointCloud* p_pc, int32_t p_i, indices_Point p_p) {
}

void indices_testPointCloud(indices_PointCloud* p_m0, indices_PointCloud p_m1) {
    indices_PointCloud l_ms = {0};
    indices_append(&l_ms, (indices_Point){1.0f, 1.0f, .05f, 1.0f});
    indices_append(&l_ms, (indices_Point){1.0f, 1.0f, .05f, 1.0f});
    const indices_Point l_p = *indices_get__PointCloud__Int(*p_m0, 10);
    indices_set__PointCloud__Int__Point(p_m0, 0, (indices_Point){1.0f, 2.0f, 3.0f, 0.0f});
    indices_get__PointCloud__Int(*p_m0, 0)->m_y = 10;
    indices_Point* tmp_ref0 = indices_get__PointCloud__Int(p_m1, 1);
    const float l_tmp = indices_get__Point__Int(*tmp_ref0, 2);
    indices_set__PointCloud__Int__Point(&l_ms, 2, *indices_get__PointCloud__Int(*p_m0, 2));
    indices_get__PointCloud__Int(l_ms, 2)->m_x = indices_get__PointCloud__Int(*p_m0, 0)->m_y;
    indices_get__PointCloud__Int(l_ms, 4)->m_x = 5;
    indices_get__PointCloud__Int(l_ms, 4)->m_y = 10;
}
