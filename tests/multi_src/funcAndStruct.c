#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct funcAndStruct_Point funcAndStruct_Point;

struct funcAndStruct_Point {
    float m_x;
    float m_y;
};

float funcAndStruct_dot(funcAndStruct_Point p_p1, funcAndStruct_Point p_p2) {
    return p_p1.m_x * p_p2.m_x + p_p1.m_y + p_p2.m_y;
}
