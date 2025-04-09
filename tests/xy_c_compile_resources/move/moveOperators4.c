#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct moveOperators4_IntList moveOperators4_IntList;

struct moveOperators4_IntList {
    char __empty_structs_are_not_allowed_in_c__;
};

int32_t* moveOperators4_get(moveOperators4_IntList p_arr, int32_t p_i) {
    return 0;
}

void moveOperators4_set(moveOperators4_IntList* p_arr, int32_t p_i, int32_t p_val) {
}

int32_t moveOperators4_func(int32_t p_num) {
    return p_num * p_num;
}

void moveOperators4_test(moveOperators4_IntList* p_a, moveOperators4_IntList* p_b, int32_t p_i, int32_t p_j) {
    int32_t* tmp_0_arg = moveOperators4_get(*p_b, p_j);
    moveOperators4_set(p_a, p_i, moveOperators4_func(*tmp_0_arg));
}
