#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct moveOperators5_Point moveOperators5_Point;
typedef struct moveOperators5_Array moveOperators5_Array;

struct moveOperators5_Point {
    int32_t m_x;
    int32_t m_y;
    int32_t m_w;
};
struct moveOperators5_Array {
    void* m_data;
};

moveOperators5_Point moveOperators5_testMovingOutInout(moveOperators5_Point* p_p) {
    moveOperators5_Point tmp_0_arg = *p_p;
    *p_p = (moveOperators5_Point){0, 0, 1};
    return tmp_0_arg;
}

moveOperators5_Point moveOperators5_testMovingSimple(void) {
    moveOperators5_Point l_p1 = {0, 0, 1};
    l_p1.m_x = 10;
    moveOperators5_Point l_p2 = {0, 0, 1};
    moveOperators5_Point tmp_0_arg = l_p1;
    l_p1 = (moveOperators5_Point){0, 0, 1};
    l_p2 = tmp_0_arg;
    return (moveOperators5_Point){l_p1.m_x, l_p2.m_y, 1};
}

void moveOperators5_dtor(moveOperators5_Array p_arr) {
}

moveOperators5_Array moveOperators5_testMovingDtor__1(void) {
    moveOperators5_Array l_arr1 = {0};
    moveOperators5_Array l_arr2 = {0};
    moveOperators5_Array tmp_0_arg = l_arr1;
    l_arr1 = (moveOperators5_Array){0};
    moveOperators5_dtor(l_arr2);
    l_arr2 = tmp_0_arg;
    moveOperators5_dtor(l_arr1);
    return l_arr2;
}

moveOperators5_Array moveOperators5_testMovingDtor__2(moveOperators5_Array p_arr) {
    moveOperators5_Array l_arr1 = {0};
    moveOperators5_dtor(l_arr1);
    return p_arr;
}
