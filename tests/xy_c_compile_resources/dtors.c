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

void* dtors_addr(dtors_Array p) {
    return p.m_mem;
}

void dtors_test1(void) {
    dtors_Array arr = (dtors_Array){0};
    dtors_push(&arr, 10);
    dtors_update(&arr);
    const int32_t tmp_err0 = dtors_errorProne(arr);
    if ((bool)tmp_err0) {
        abort();
    }
    dtors_Array tmp_arg1 = dtors_funcReturningAnObjectWithDtor(10);
    const int32_t tmp_err2 = dtors_errorProne(tmp_arg1);
    if ((bool)tmp_err2) {
        abort();
    }
    dtors_dtor(tmp_arg1, true);
    dtors_dtor(arr, true);
}

int32_t dtors_test2(int32_t rng) {
    dtors_Array arr1 = (dtors_Array){0};
    const int32_t tmp_err0 = dtors_errorProne(arr1);
    if ((bool)tmp_err0) {
        dtors_dtor(arr1, true);
        return tmp_err0;
    }
    dtors_Array arr2 = (dtors_Array){0};
    const int32_t tmp_err1 = dtors_errorProne(arr2);
    if ((bool)tmp_err1) {
        dtors_dtor(arr2, true);
        dtors_dtor(arr1, true);
        return tmp_err1;
    }
    dtors_Array arr3 = (dtors_Array){0};
    dtors_dtor(arr3, true);
    dtors_dtor(arr2, true);
    dtors_dtor(arr1, true);
    return 0;
}

int32_t dtors_test3(int32_t rng, dtors_Array* _res0) {
    dtors_Array arr1 = (dtors_Array){0};
    const int32_t tmp_err0 = dtors_errorProne(arr1);
    if ((bool)tmp_err0) {
        dtors_dtor(arr1, true);
        return tmp_err0;
    }
    dtors_Array arr2 = (dtors_Array){0};
    const int32_t tmp_err1 = dtors_errorProne(arr2);
    if ((bool)tmp_err1) {
        dtors_dtor(arr2, true);
        dtors_dtor(arr1, true);
        return tmp_err1;
    }
    dtors_Array arr3 = (dtors_Array){0};
    dtors_Array tmp3 = (dtors_Array){0};
    if (rng == 0) {
        tmp3 = arr1;
    } else if (rng == 1) {
        tmp3 = arr2;
    } else {
        tmp3 = arr3;
    }
    *_res0 = tmp3;
    dtors_dtor(arr3, true);
    dtors_dtor(arr2, true);
    dtors_dtor(arr1, true);
    return 0;
}

int32_t dtors_test4(int32_t rng, dtors_Array* _res0) {
    dtors_Array arr1 = (dtors_Array){0};
    const int32_t tmp_err0 = dtors_errorProne(arr1);
    if ((bool)tmp_err0) {
        dtors_dtor(arr1, true);
        return tmp_err0;
    }
    int32_t num = 10;
    while (rng < num) {
        dtors_Array arr2 = (dtors_Array){0};
        const int32_t tmp_err0 = dtors_errorProne(arr2);
        if ((bool)tmp_err0) {
            dtors_dtor(arr2, true);
            dtors_dtor(arr1, true);
            return tmp_err0;
        }
        for (int32_t i = 0; i < num; ++i) {
            dtors_Array arr3 = (dtors_Array){0};
            const int32_t tmp_err0 = dtors_errorProne(arr3);
            if ((bool)tmp_err0) {
                dtors_dtor(arr3, true);
                dtors_dtor(arr2, true);
                dtors_dtor(arr1, true);
                return tmp_err0;
            }
            if (i == rng * 2) {
                dtors_Array arr4 = (dtors_Array){0};
                *_res0 = arr1;
                dtors_dtor(arr4, true);
                dtors_dtor(arr3, true);
                dtors_dtor(arr2, true);
                return 0;
            }
            if (rng == 3) {
                dtors_Array arr4 = (dtors_Array){0};
                dtors_dtor(arr4, true);
                dtors_dtor(arr3, true);
                break;
            }
            dtors_dtor(arr3, true);
        }
        num--;
        dtors_dtor(arr2, true);
    }
    *_res0 = (dtors_Array){0};
    return 0;
}

dtors_Array dtors_test5(int32_t rng) {
    dtors_Array arrs[10] = {};
    dtors_Array tmp_res0 = arrs[rng];
    for (size_t _i = 0; _i < 10; ++_i) {
        dtors_dtor(arrs[_i], true);
    }
    return tmp_res0;
}
