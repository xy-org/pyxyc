#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct moveOperators7_Elem moveOperators7_Elem;
typedef struct moveOperators7_Array moveOperators7_Array;

struct moveOperators7_Elem {
    int32_t m_val;
};
struct moveOperators7_Array {
    moveOperators7_Elem* m_mem;
};

void moveOperators7_dtor__Elem(moveOperators7_Elem p_e) {
}

moveOperators7_Elem* moveOperators7_get(moveOperators7_Array p_arr, int32_t p_idx) {
    return p_arr.m_mem;
}

void moveOperators7_set(moveOperators7_Array p_arr, int32_t p_idx, moveOperators7_Elem p_elem) {
}

void moveOperators7_dtor__Array(moveOperators7_Array p_arr) {
}

void moveOperators7_test1(moveOperators7_Array* p_arr, int32_t p_i, int32_t p_j) {
    moveOperators7_Elem* tmp_0_arg = moveOperators7_get(*p_arr, p_j);
    moveOperators7_Elem tmp_1_ref = *tmp_0_arg;
    moveOperators7_set(*p_arr, p_j, (moveOperators7_Elem){0});
    moveOperators7_Elem* tmp_2_arg = moveOperators7_get(*p_arr, p_i);
    moveOperators7_dtor__Elem(*tmp_2_arg);
    *tmp_2_arg = (moveOperators7_Elem){0};
    moveOperators7_set(*p_arr, p_i, tmp_1_ref);
}

void moveOperators7_test2(moveOperators7_Array* p_arr, int32_t p_i) {
    moveOperators7_Elem* tmp_0_arg = moveOperators7_get(*p_arr, p_i);
    moveOperators7_dtor__Elem(*tmp_0_arg);
    *tmp_0_arg = (moveOperators7_Elem){0};
    moveOperators7_set(*p_arr, p_i, (moveOperators7_Elem){0});
}

void moveOperators7_test3(moveOperators7_Array* p_arr, int32_t p_i) {
    moveOperators7_Elem* tmp_0_arg = moveOperators7_get(*p_arr, p_i);
    *tmp_0_arg = (moveOperators7_Elem){0};
}
