#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct dtors2_Array dtors2_Array;

struct dtors2_Array {
    void* m_mem;
    size_t m_len;
};

void dtors2_dtor(dtors2_Array* arr) {
}

void dtors2_test(void) {
    dtors2_Array arr1 = (dtors2_Array){0};
    dtors2_Array arr2 = (dtors2_Array){0};
    dtors2_Array arr3 = (dtors2_Array){0};
    dtors2_Array arr4 = (dtors2_Array){0};
    const dtors2_Array arr5 = (dtors2_Array){0, 10};
    dtors2_dtor(&arr5);
    dtors2_dtor(&arr4);
    dtors2_dtor(&arr3);
    dtors2_dtor(&arr2);
    dtors2_dtor(&arr1);
}
