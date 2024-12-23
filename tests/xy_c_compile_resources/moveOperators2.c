#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct moveOperators2_IntList moveOperators2_IntList;

struct moveOperators2_IntList {
    char __empty_structs_are_not_allowed_in_c__;
};

int32_t* moveOperators2_get(moveOperators2_IntList arr, int32_t i) {
    return 0;
}

void moveOperators2_set(moveOperators2_IntList* arr, int32_t i, int32_t val) {
}

void moveOperators2_test(moveOperators2_IntList* a, moveOperators2_IntList* b, int32_t i, int32_t j) {
    int32_t tmp_ref0 = *moveOperators2_get(*b, j);
    moveOperators2_set(b, j, 0);
    moveOperators2_set(a, i, tmp_ref0);
}
