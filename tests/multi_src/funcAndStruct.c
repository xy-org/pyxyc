#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct funcAndStruct_Point funcAndStruct_Point;

struct funcAndStruct_Point {
    float xy_x;
    float xy_y;
};

float funcAndStruct_dot(funcAndStruct_Point p1, funcAndStruct_Point p2) {
    return p1.xy_x * p2.xy_x + p1.xy_y + p2.xy_y;
}
