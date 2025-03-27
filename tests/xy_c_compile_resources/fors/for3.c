#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct for3_Array for3_Array;

struct for3_Array {
    float m_elems[100];
    size_t m_len;
};

size_t for3_iter(void) {
    return 0;
}

void for3_next(size_t* p_idx) {
    (*p_idx)++;
}

float* for3_get(for3_Array* p_arr, size_t p_idx) {
    return &p_arr->m_elems[p_idx];
}

void for3_set(for3_Array* p_arr, size_t p_idx, float p_elem) {
    p_arr->m_elems[p_idx] = p_elem;
}

float for3_sum(for3_Array p_arr) {
    float l_res = 0;
    for (size_t tmp_0_iter = for3_iter(); tmp_0_iter < p_arr.m_len; for3_next(&tmp_0_iter)) {
        if (!(tmp_0_iter < p_arr.m_len)) {
            abort();
        }
        float* tmp_1_ref = for3_get(&p_arr, tmp_0_iter);
        l_res += *tmp_1_ref;
    }
    return l_res;
}

float for3_mix(for3_Array p_arr1, for3_Array p_arr2) {
    float l_res = 0;
    {
        uint32_t i = 0;
        size_t tmp_0_iter = for3_iter();
        size_t tmp_1_iter = for3_iter();
        for (; tmp_0_iter < p_arr1.m_len && tmp_1_iter < p_arr2.m_len; ++i, for3_next(&tmp_0_iter), for3_next(&tmp_1_iter)) {
            if (!(tmp_0_iter < p_arr1.m_len)) {
                abort();
            }
            float* tmp_2_ref = for3_get(&p_arr1, tmp_0_iter);
            if (!(tmp_1_iter < p_arr2.m_len)) {
                abort();
            }
            float* tmp_3_ref = for3_get(&p_arr2, tmp_1_iter);
            l_res += i * *tmp_2_ref * *tmp_3_ref;
        }
    }
    return l_res;
}

void for3_double(for3_Array* p_arr1) {
    for (size_t tmp_0_iter = for3_iter(); tmp_0_iter < p_arr1->m_len; for3_next(&tmp_0_iter)) {
        if (!(tmp_0_iter < p_arr1->m_len)) {
            abort();
        }
        if (*for3_get(p_arr1, tmp_0_iter) > 0) {
            if (!(tmp_0_iter < p_arr1->m_len)) {
                abort();
            }
            float* tmp_2_ref = for3_get(p_arr1, tmp_0_iter);
            for3_set(p_arr1, tmp_0_iter, 2.0f * *tmp_2_ref);
            if (!(tmp_0_iter < p_arr1->m_len)) {
                abort();
            }
            float* tmp_3_ref = for3_get(p_arr1, tmp_0_iter);
            if (!(tmp_0_iter < p_arr1->m_len)) {
                abort();
            }
            float* tmp_4_ref = for3_get(p_arr1, tmp_0_iter);
            *tmp_3_ref += *tmp_4_ref;
        }
    }
}

void for3_doSomething(float p_f) {
}

void for3_changeSomehow(float* p_f) {
}

void for3_iterAndChange(for3_Array* p_arr1) {
    for (size_t tmp_0_iter = for3_iter(); tmp_0_iter < p_arr1->m_len; for3_next(&tmp_0_iter)) {
        if (!(tmp_0_iter < p_arr1->m_len)) {
            abort();
        }
        float* tmp_1_ref = for3_get(p_arr1, tmp_0_iter);
        for3_doSomething(*tmp_1_ref);
        if (!(tmp_0_iter < p_arr1->m_len)) {
            abort();
        }
        float* tmp_2_ref = for3_get(p_arr1, tmp_0_iter);
        for3_changeSomehow(tmp_2_ref);
    }
}
