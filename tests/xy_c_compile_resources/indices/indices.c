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
    uint64_t m_len;
};

int32_t indices_select__1(indices_Point p_p, int32_t p_idx) {
    return p_idx;
}

float indices_get__1(indices_Point p_p, int32_t p_idx) {
    return (float[4]){p_p.m_x, p_p.m_y, p_p.m_z, p_p.m_w}[p_idx];
}

void indices_set__1(indices_Point* p_p, int32_t p_idx, float p_v) {
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
    l_p1.m_x = indices_get__1(l_p1, p_i);
    l_p2.m_z = indices_get__1(l_p1, 4 - p_i);
    float tmp_0_arg = l_p1.m_x + indices_get__1(l_p2, 2) + l_p2.m_z;
    const float l_sum = tmp_0_arg + indices_get__1(l_p1, 3);
    float l_res = indices_get__1(l_p1, 0);
    float tmp_1_arg = indices_get__1(l_p1, 0);
    if (!(0 <= 3)) {
        abort();
    }
    indices_set__1(&l_p2, 0, tmp_1_arg);
    l_res += indices_get__1(l_p2, 0);
    return l_res + l_sum;
}

void indices_append(indices_PointCloud* p_pc, indices_Point p_p) {
    p_pc->m_len++;
}

int32_t indices_select__2(indices_PointCloud p_pc, int32_t p_i) {
    return p_i;
}

indices_Point* indices_get__2(indices_PointCloud p_pc, int32_t p_i) {
    return (indices_Point*)((int8_t*)p_pc.m_mem + (uint64_t)p_i * sizeof(indices_Point));
}

void indices_set__2(indices_PointCloud* p_pc, int32_t p_i, indices_Point p_p) {
}

void indices_testPointCloud(indices_PointCloud* p_m0, indices_PointCloud p_m1) {
    indices_PointCloud l_ms = {0};
    indices_append(&l_ms, (indices_Point){1.0f, 1.0f, .05f, 1.0f});
    indices_append(&l_ms, (indices_Point){1.0f, 1.0f, .05f, 1.0f});
    indices_Point* tmp_0_arg = indices_get__2(*p_m0, 10);
    const indices_Point l_p = *tmp_0_arg;
    indices_set__2(p_m0, 0, (indices_Point){1.0f, 2.0f, 3.0f, 0.0f});
    indices_Point* tmp_1_arg = indices_get__2(*p_m0, 0);
    tmp_1_arg->m_y = 10.0f;
    indices_Point* tmp_2_arg = indices_get__2(p_m1, 1);
    const float l_tmp = indices_get__1(*tmp_2_arg, 2);
    indices_Point* tmp_3_arg = indices_get__2(*p_m0, 2);
    indices_set__2(&l_ms, 2, *tmp_3_arg);
    indices_Point* tmp_4_arg = indices_get__2(*p_m0, 0);
    indices_Point* tmp_5_arg = indices_get__2(l_ms, 2);
    tmp_5_arg->m_x = tmp_4_arg->m_y;
    indices_Point* tmp_6_arg = indices_get__2(l_ms, 4);
    tmp_6_arg->m_x = 5.0f;
    tmp_6_arg->m_y = 10.0f;
}
