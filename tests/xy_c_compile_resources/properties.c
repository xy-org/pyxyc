#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct properties_Vec2 properties_Vec2;
typedef struct properties_Pair properties_Pair;

struct properties_Vec2 {
    float m_coords[2];
};
struct properties_Pair {
    int32_t m_i;
    int32_t m_j;
};

void properties_test(void) {
    properties_Vec2 tmp_0 = (properties_Vec2){0};
    tmp_0.m_coords[0] = .23f;
    tmp_0.m_coords[1] = .92f;
    properties_Vec2 l_p1 = tmp_0;
    properties_Vec2 tmp_1 = (properties_Vec2){0};
    tmp_1.m_coords[0] = .4837f;
    tmp_1.m_coords[1] = .127f;
    properties_Vec2 l_p2 = tmp_1;
    properties_Vec2 tmp_2 = (properties_Vec2){0};
    tmp_2.m_coords[0] = l_p1.m_coords[(properties_Pair){1, 0}.m_i];
    tmp_2.m_coords[1] = l_p1.m_coords[(properties_Pair){1, 0}.m_j];
    const properties_Vec2 l_p3 = tmp_2;
    l_p1.m_coords[0] = l_p2.m_coords[1];
    l_p2.m_coords[1] = .0f;
    const float l_mix = (l_p1.m_coords[0] - l_p2.m_coords[0]) * (l_p1.m_coords[0] - l_p2.m_coords[0]) + (l_p1.m_coords[1] - l_p3.m_coords[1]) * (l_p1.m_coords[1] - l_p3.m_coords[1]);
}
