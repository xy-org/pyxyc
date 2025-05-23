#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct dtors2_Array dtors2_Array;

struct dtors2_Array {
    void* m_mem;
    size_t m_len;
};

void dtors2_dtor(dtors2_Array* p_arr) {
}

void dtors2_test(void) {
    dtors2_Array l_arr1 = {0};
    dtors2_Array l_arr2 = {0};
    dtors2_Array l_arr3 = {0};
    dtors2_Array l_arr4 = {0};
    const dtors2_Array l_arr5 = {0, (size_t)10};
    dtors2_dtor(&l_arr5);
    dtors2_dtor(&l_arr4);
    dtors2_dtor(&l_arr3);
    dtors2_dtor(&l_arr2);
    dtors2_dtor(&l_arr1);
}
