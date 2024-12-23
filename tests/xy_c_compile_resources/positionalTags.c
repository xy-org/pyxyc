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

size_t positionalTags_len(positionalTags_Array arr) {
    return arr.m_len;
}

int32_t positionalTags_sizeof__int(void) {
    return 4;
}

int32_t positionalTags_sizeof__Point(void) {
    return 8;
}

int32_t positionalTags_test(void) {
    positionalTags_Array ints = (positionalTags_Array){0};
    positionalTags_Array points = (positionalTags_Array){0};
    return positionalTags_len(ints) + positionalTags_len(points) + positionalTags_sizeof__int() + positionalTags_sizeof__Point();
}
