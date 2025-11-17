#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct moveOperators2_IntList moveOperators2_IntList;

struct moveOperators2_IntList {
    void* m_data;
};

int32_t* moveOperators2_get(moveOperators2_IntList p_arr, int32_t p_i) {
    return 0;
}

void moveOperators2_set(moveOperators2_IntList* p_arr, int32_t p_i, int32_t p_val) {
}

void moveOperators2_test(moveOperators2_IntList* p_a, moveOperators2_IntList* p_b, int32_t p_i, int32_t p_j) {
    int32_t* tmp_0_arg = moveOperators2_get(*p_b, p_j);
    int32_t tmp_1_ref = *tmp_0_arg;
    *tmp_0_arg = 0;
    moveOperators2_set(p_a, p_i, tmp_1_ref);
}
