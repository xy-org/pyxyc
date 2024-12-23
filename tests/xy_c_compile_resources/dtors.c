#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct dtors_Array dtors_Array;

struct dtors_Array {
    void* m_mem;
};

void dtors_free(void* mem) {
}

void dtors_push(dtors_Array* arr, int32_t val) {
}

void dtors_dtor(dtors_Array p, bool managed) {
    if (managed) {
        dtors_free(p.m_mem);
    }
}

void dtors_update(dtors_Array* arr) {
}

int32_t dtors_errorProne(dtors_Array arr) {
    return 0;
}

dtors_Array dtors_funcReturningAnObjectWithDtor(int32_t num) {
    dtors_Array arr = (dtors_Array){0};
    for (int32_t i = 0; i < num; ++i) {
        dtors_push(&arr, i);
    }
    return arr;
}

void dtors_addr(dtors_Array p) {
    return p.m_mem;
}

void dtors_test(void) {
    dtors_Array arr = (dtors_Array){0};
    dtors_push(&arr, 10);
    dtors_update(&arr);
    dtors_update(&dtors_funcReturningAnObjectWithDtor(10));
    const int32_t tmp_err0 = dtors_errorProne(arr);
    if ((bool)tmp_err0) {
        abort();
    }
    dtors_dtor(arr, true);
}
