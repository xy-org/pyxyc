#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct positionalTags_Array positionalTags_Array;
typedef struct positionalTags_Point positionalTags_Point;

struct positionalTags_Array {
    size_t m_len;
};
struct positionalTags_Point {
    float m_x;
    float m_y;
};

int32_t positionalTags_test(void) {
    positionalTags_Array ints = (positionalTags_Array){0};
    positionalTags_Array points = (positionalTags_Array){0};
    return ints.m_len + points.m_len + 4 + 8;
}
