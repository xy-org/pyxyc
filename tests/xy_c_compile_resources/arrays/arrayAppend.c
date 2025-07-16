#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct arrayAppend__EMPTY_STRUCT_ arrayAppend_Array;

struct arrayAppend__EMPTY_STRUCT_ {
    char __empty_structs_are_not_allowed_in_c__;
};

void arrayAppend_append(arrayAppend_Array* p_arr, int32_t p_val) {
}

arrayAppend_Array arrayAppend_copy(arrayAppend_Array* p_arr) {
    return (arrayAppend_Array){0};
}

arrayAppend_Array arrayAppend_test(arrayAppend_Array* p_arr) {
    arrayAppend_append(p_arr, 1);
    arrayAppend_append(p_arr, 2);
    arrayAppend_append(p_arr, 3);
    arrayAppend_append(p_arr, 4);
    arrayAppend_Array tmp_0_comp = arrayAppend_copy(p_arr);
    arrayAppend_append(&tmp_0_comp, 5);
    arrayAppend_append(&tmp_0_comp, 6);
    return tmp_0_comp;
}
