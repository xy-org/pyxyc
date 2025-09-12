#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct dtors1_Array dtors1_Array;

struct dtors1_Array {
    void* m_mem;
};

void dtors1_free(void* p_mem) {
}

void dtors1_push(dtors1_Array* p_arr, int32_t p_val) {
}

void dtors1_dtor(dtors1_Array p_p, bool p_managed) {
    if (p_managed) {
        dtors1_free(p_p.m_mem);
    }
}

void dtors1_update(dtors1_Array* p_arr) {
}

int32_t dtors1_errorProne(dtors1_Array p_arr) {
    return 0;
}

dtors1_Array dtors1_funcReturningAnObjectWithDtor(int32_t p_num) {
    dtors1_Array l_arr = {0};
    for (int32_t i = 0; i < p_num; ++i) {
        dtors1_push(&l_arr, i);
    }
    return l_arr;
}

void* dtors1_addr(dtors1_Array p_p) {
    return p_p.m_mem;
}

void dtors1_test1(void) {
    dtors1_Array l_arr = {0};
    dtors1_push(&l_arr, 10);
    dtors1_update(&l_arr);
    const int32_t tmp_0_err = dtors1_errorProne(l_arr);
    if ((bool)tmp_0_err) {
        abort();
    }
    dtors1_Array tmp_1_arg = dtors1_funcReturningAnObjectWithDtor(10);
    const int32_t tmp_2_err = dtors1_errorProne(tmp_1_arg);
    if ((bool)tmp_2_err) {
        abort();
    }
    dtors1_dtor(tmp_1_arg, true);
    dtors1_dtor(l_arr, true);
}

int32_t dtors1_test2(int32_t p_rng) {
    dtors1_Array l_arr1 = {0};
    const int32_t tmp_0_err = dtors1_errorProne(l_arr1);
    if ((bool)tmp_0_err) {
        dtors1_dtor(l_arr1, true);
        return tmp_0_err;
    }
    dtors1_Array l_arr2 = {0};
    const int32_t tmp_1_err = dtors1_errorProne(l_arr2);
    if ((bool)tmp_1_err) {
        dtors1_dtor(l_arr2, true);
        dtors1_dtor(l_arr1, true);
        return tmp_1_err;
    }
    dtors1_Array l_arr3 = {0};
    dtors1_dtor(l_arr3, true);
    dtors1_dtor(l_arr2, true);
    dtors1_dtor(l_arr1, true);
    return 0;
}

int32_t dtors1_test3(int32_t p_rng, dtors1_Array* _res0) {
    dtors1_Array l_arr1 = {0};
    const int32_t tmp_0_err = dtors1_errorProne(l_arr1);
    if ((bool)tmp_0_err) {
        dtors1_dtor(l_arr1, true);
        return tmp_0_err;
    }
    dtors1_Array l_arr2 = {0};
    const int32_t tmp_1_err = dtors1_errorProne(l_arr2);
    if ((bool)tmp_1_err) {
        dtors1_dtor(l_arr2, true);
        dtors1_dtor(l_arr1, true);
        return tmp_1_err;
    }
    dtors1_Array l_arr3 = {0};
    dtors1_Array tmp_2 = (dtors1_Array){0};
    if (p_rng == 0) {
        tmp_2 = l_arr1;
    } else if (p_rng == 1) {
        tmp_2 = l_arr2;
    } else {
        tmp_2 = l_arr3;
    }
    *_res0 = tmp_2;
    dtors1_dtor(l_arr3, true);
    dtors1_dtor(l_arr2, true);
    dtors1_dtor(l_arr1, true);
    return 0;
}

int32_t dtors1_test4(int32_t p_rng, dtors1_Array* _res0) {
    dtors1_Array l_arr1 = {0};
    const int32_t tmp_0_err = dtors1_errorProne(l_arr1);
    if ((bool)tmp_0_err) {
        dtors1_dtor(l_arr1, true);
        return tmp_0_err;
    }
    int32_t l_num = 10;
    while (p_rng < l_num) {
        dtors1_Array l_arr2 = {0};
        const int32_t tmp_1_err = dtors1_errorProne(l_arr2);
        if ((bool)tmp_1_err) {
            dtors1_dtor(l_arr2, true);
            dtors1_dtor(l_arr1, true);
            return tmp_1_err;
        }
        for (int32_t i = 0; i < l_num; ++i) {
            dtors1_Array l_arr3 = {0};
            const int32_t tmp_2_err = dtors1_errorProne(l_arr3);
            if ((bool)tmp_2_err) {
                dtors1_dtor(l_arr3, true);
                dtors1_dtor(l_arr2, true);
                dtors1_dtor(l_arr1, true);
                return tmp_2_err;
            }
            if (i == p_rng * 2) {
                dtors1_Array l_arr4 = {0};
                *_res0 = l_arr1;
                dtors1_dtor(l_arr4, true);
                dtors1_dtor(l_arr3, true);
                dtors1_dtor(l_arr2, true);
                return 0;
            }
            if (p_rng == 3) {
                dtors1_Array l_arr4 = {0};
                dtors1_dtor(l_arr4, true);
                l_arr4 = (dtors1_Array){0};
                dtors1_dtor(l_arr3, true);
                l_arr3 = (dtors1_Array){0};
                break;
            }
            dtors1_dtor(l_arr3, true);
        }
        l_num--;
        dtors1_dtor(l_arr2, true);
    }
    *_res0 = (dtors1_Array){0};
    return 0;
}

dtors1_Array dtors1_test5(int32_t p_rng) {
    dtors1_Array l_arrs[10] = {0};
    dtors1_Array tmp_0_res = l_arrs[p_rng];
    for (size_t _i = 0; _i < 10; ++_i) {
        dtors1_dtor(l_arrs[_i], true);
    }
    return tmp_0_res;
}
