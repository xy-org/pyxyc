#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct positionalTags_Array positionalTags_Array;
typedef struct positionalTags_Point positionalTags_Point;

struct positionalTags_Array {
    uint64_t m_len;
};
struct positionalTags_Point {
    float m_x;
    float m_y;
};

uint64_t positionalTags_test(void) {
    positionalTags_Array l_ints = {0};
    positionalTags_Array l_points = {0};
    return l_ints.m_len + l_points.m_len + 4 + 8;
}
