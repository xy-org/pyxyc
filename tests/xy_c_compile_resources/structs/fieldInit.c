#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct fieldInit_Vec4 fieldInit_Vec4;

struct fieldInit_Vec4 {
    int32_t m_x;
    int32_t m_y;
    int32_t m_z;
    int32_t m_w;
};

void fieldInit_test(void) {
    const fieldInit_Vec4 l_p0 = {0, 1, 2, 3};
    const fieldInit_Vec4 l_p1 = {10, 1, 2, 3};
    const fieldInit_Vec4 l_p2 = {10, 20, 2, 3};
    const fieldInit_Vec4 l_p3 = {0, 1, 2, 30};
}
