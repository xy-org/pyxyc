#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct funcAndStruct_Point funcAndStruct_Point;

struct funcAndStruct_Point {
    float x;
    float y;
};

float funcAndStruct_dot(funcAndStruct_Point p1, funcAndStruct_Point p2) {
    return p1.x * p2.x + p1.y + p2.y;
}
