#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct arrayAppendEnum__EMPTY_STRUCT_ arrayAppendEnum_Array;

struct arrayAppendEnum__EMPTY_STRUCT_ {
    char __empty_structs_are_not_allowed_in_c__;
};

void arrayAppendEnum_append(arrayAppendEnum_Array* p_arr, int32_t p_dim1, int32_t p_dim2, int32_t p_dim3) {
}

void arrayAppendEnum_test(arrayAppendEnum_Array* p_arr) {
    arrayAppendEnum_append(p_arr, 2, 3, 4);
}
