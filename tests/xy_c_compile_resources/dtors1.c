#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct dtors1_Array dtors1_Array;

struct dtors1_Array {
    void* m_mem;
};

void dtors1_free(void* mem) {
}

void dtors1_push(dtors1_Array* arr, int32_t val) {
}

void dtors1_dtor(dtors1_Array p, bool managed) {
    if (managed) {
        dtors1_free(p.m_mem);
    }
}

void dtors1_update(dtors1_Array* arr) {
}

int32_t dtors1_errorProne(dtors1_Array arr) {
    return 0;
}

dtors1_Array dtors1_funcReturningAnObjectWithDtor(int32_t num) {
    dtors1_Array arr = (dtors1_Array){0};
    for (int32_t i = 0; i < num; ++i) {
        dtors1_push(&arr, i);
    }
    return arr;
}

void* dtors1_addr(dtors1_Array p) {
    return p.m_mem;
}

void dtors1_test1(void) {
    dtors1_Array arr = (dtors1_Array){0};
    dtors1_push(&arr, 10);
    dtors1_update(&arr);
    const int32_t tmp_err0 = dtors1_errorProne(arr);
    if ((bool)tmp_err0) {
        abort();
    }
    dtors1_Array tmp_arg1 = dtors1_funcReturningAnObjectWithDtor(10);
    const int32_t tmp_err2 = dtors1_errorProne(tmp_arg1);
    if ((bool)tmp_err2) {
        abort();
    }
    dtors1_dtor(tmp_arg1, true);
    dtors1_dtor(arr, true);
}

int32_t dtors1_test2(int32_t rng) {
    dtors1_Array arr1 = (dtors1_Array){0};
    const int32_t tmp_err0 = dtors1_errorProne(arr1);
    if ((bool)tmp_err0) {
        dtors1_dtor(arr1, true);
        return tmp_err0;
    }
    dtors1_Array arr2 = (dtors1_Array){0};
    const int32_t tmp_err1 = dtors1_errorProne(arr2);
    if ((bool)tmp_err1) {
        dtors1_dtor(arr2, true);
        dtors1_dtor(arr1, true);
        return tmp_err1;
    }
    dtors1_Array arr3 = (dtors1_Array){0};
    dtors1_dtor(arr3, true);
    dtors1_dtor(arr2, true);
    dtors1_dtor(arr1, true);
    return 0;
}

int32_t dtors1_test3(int32_t rng, dtors1_Array* _res0) {
    dtors1_Array arr1 = (dtors1_Array){0};
    const int32_t tmp_err0 = dtors1_errorProne(arr1);
    if ((bool)tmp_err0) {
        dtors1_dtor(arr1, true);
        return tmp_err0;
    }
    dtors1_Array arr2 = (dtors1_Array){0};
    const int32_t tmp_err1 = dtors1_errorProne(arr2);
    if ((bool)tmp_err1) {
        dtors1_dtor(arr2, true);
        dtors1_dtor(arr1, true);
        return tmp_err1;
    }
    dtors1_Array arr3 = (dtors1_Array){0};
    dtors1_Array tmp3 = (dtors1_Array){0};
    if (rng == 0) {
        tmp3 = arr1;
    } else if (rng == 1) {
        tmp3 = arr2;
    } else {
        tmp3 = arr3;
    }
    *_res0 = tmp3;
    dtors1_dtor(arr3, true);
    dtors1_dtor(arr2, true);
    dtors1_dtor(arr1, true);
    return 0;
}

int32_t dtors1_test4(int32_t rng, dtors1_Array* _res0) {
    dtors1_Array arr1 = (dtors1_Array){0};
    const int32_t tmp_err0 = dtors1_errorProne(arr1);
    if ((bool)tmp_err0) {
        dtors1_dtor(arr1, true);
        return tmp_err0;
    }
    int32_t num = 10;
    while (rng < num) {
        dtors1_Array arr2 = (dtors1_Array){0};
        const int32_t tmp_err0 = dtors1_errorProne(arr2);
        if ((bool)tmp_err0) {
            dtors1_dtor(arr2, true);
            dtors1_dtor(arr1, true);
            return tmp_err0;
        }
        for (int32_t i = 0; i < num; ++i) {
            dtors1_Array arr3 = (dtors1_Array){0};
            const int32_t tmp_err0 = dtors1_errorProne(arr3);
            if ((bool)tmp_err0) {
                dtors1_dtor(arr3, true);
                dtors1_dtor(arr2, true);
                dtors1_dtor(arr1, true);
                return tmp_err0;
            }
            if (i == rng * 2) {
                dtors1_Array arr4 = (dtors1_Array){0};
                *_res0 = arr1;
                dtors1_dtor(arr4, true);
                dtors1_dtor(arr3, true);
                dtors1_dtor(arr2, true);
                return 0;
            }
            if (rng == 3) {
                dtors1_Array arr4 = (dtors1_Array){0};
                dtors1_dtor(arr4, true);
                dtors1_dtor(arr3, true);
                break;
            }
            dtors1_dtor(arr3, true);
        }
        num--;
        dtors1_dtor(arr2, true);
    }
    *_res0 = (dtors1_Array){0};
    return 0;
}

dtors1_Array dtors1_test5(int32_t rng) {
    dtors1_Array arrs[10] = {};
    dtors1_Array tmp_res0 = arrs[rng];
    for (size_t _i = 0; _i < 10; ++_i) {
        dtors1_dtor(arrs[_i], true);
    }
    return tmp_res0;
}
