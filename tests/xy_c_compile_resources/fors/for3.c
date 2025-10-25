#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct for3_Array for3_Array;

struct for3_Array {
    float m_elems[100];
    uint64_t m_len;
};

uint64_t for3_iter(void) {
    return 0;
}

void for3_next(uint64_t* p_idx) {
    (*p_idx)++;
}

float* for3_get(for3_Array* p_arr, uint64_t p_idx) {
    return &p_arr->m_elems[p_idx];
}

void for3_set(for3_Array* p_arr, uint64_t p_idx, float p_elem) {
    p_arr->m_elems[p_idx] = p_elem;
}

float for3_sum(for3_Array* p_arr) {
    uint64_t tmp_0_arg = for3_iter();
    float l_res = 0;
    for (uint64_t tmp_1_iter = tmp_0_arg; tmp_1_iter < p_arr->m_len; for3_next(&tmp_1_iter)) {
        if (!(tmp_1_iter < p_arr->m_len)) {
            abort();
        }
        float* tmp_2_arg = for3_get(p_arr, tmp_1_iter);
        l_res += *tmp_2_arg;
    }
    return l_res;
}

float for3_mix(for3_Array* p_arr1, for3_Array* p_arr2) {
    uint64_t tmp_0_arg = for3_iter();
    uint64_t tmp_2_arg = for3_iter();
    float l_res = 0;
    {
        uint32_t i = 0;
        uint64_t tmp_1_iter = tmp_0_arg;
        uint64_t tmp_3_iter = tmp_2_arg;
        for (; tmp_1_iter < p_arr1->m_len && tmp_3_iter < p_arr2->m_len; ++i, for3_next(&tmp_1_iter), for3_next(&tmp_3_iter)) {
            if (!(tmp_1_iter < p_arr1->m_len)) {
                abort();
            }
            float* tmp_4_arg = for3_get(p_arr1, tmp_1_iter);
            if (!(tmp_3_iter < p_arr2->m_len)) {
                abort();
            }
            float* tmp_5_arg = for3_get(p_arr2, tmp_3_iter);
            l_res += (float)i * *tmp_4_arg * *tmp_5_arg;
        }
    }
    return l_res;
}

void for3_double(for3_Array* p_arr1) {
    uint64_t tmp_0_arg = for3_iter();
    for (uint64_t tmp_1_iter = tmp_0_arg; tmp_1_iter < p_arr1->m_len; for3_next(&tmp_1_iter)) {
        if (!(tmp_1_iter < p_arr1->m_len)) {
            abort();
        }
        float* tmp_2_arg = for3_get(p_arr1, tmp_1_iter);
        if (*tmp_2_arg > 0) {
            if (!(tmp_1_iter < p_arr1->m_len)) {
                abort();
            }
            float* tmp_3_arg = for3_get(p_arr1, tmp_1_iter);
            for3_set(p_arr1, tmp_1_iter, 2.0f * *tmp_3_arg);
            if (!(tmp_1_iter < p_arr1->m_len)) {
                abort();
            }
            float* tmp_4_arg = for3_get(p_arr1, tmp_1_iter);
            if (!(tmp_1_iter < p_arr1->m_len)) {
                abort();
            }
            float* tmp_5_arg = for3_get(p_arr1, tmp_1_iter);
            for3_set(p_arr1, tmp_1_iter, *tmp_5_arg + *tmp_4_arg);
        }
    }
}

void for3_doSomething(float p_f) {
}

void for3_changeSomehow(float* p_f) {
}

void for3_iterAndChange(for3_Array* p_arr1) {
    uint64_t tmp_0_arg = for3_iter();
    for (uint64_t tmp_1_iter = tmp_0_arg; tmp_1_iter < p_arr1->m_len; for3_next(&tmp_1_iter)) {
        if (!(tmp_1_iter < p_arr1->m_len)) {
            abort();
        }
        float* tmp_2_arg = for3_get(p_arr1, tmp_1_iter);
        for3_doSomething(*tmp_2_arg);
        if (!(tmp_1_iter < p_arr1->m_len)) {
            abort();
        }
        float* tmp_3_arg = for3_get(p_arr1, tmp_1_iter);
        for3_changeSomehow(tmp_3_arg);
    }
}
