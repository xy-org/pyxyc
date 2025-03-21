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
    for (size_t tmp_iter0 = for3_iter(); tmp_iter0 < p_arr.m_len; for3_next(&tmp_iter0)) {
        if (!(tmp_iter0 < p_arr.m_len)) {
            abort();
        }
        float* tmp_ref1 = for3_get(&p_arr, tmp_iter0);
        l_res += *tmp_ref1;
    }
    return l_res;
}

float for3_mix(for3_Array p_arr1, for3_Array p_arr2) {
    float l_res = 0;
    {
        uint32_t i = 0;
        size_t tmp_iter0 = for3_iter();
        size_t tmp_iter1 = for3_iter();
        for (; tmp_iter0 < p_arr1.m_len && tmp_iter1 < p_arr2.m_len; ++i, for3_next(&tmp_iter0), for3_next(&tmp_iter1)) {
            if (!(tmp_iter0 < p_arr1.m_len)) {
                abort();
            }
            float* tmp_ref2 = for3_get(&p_arr1, tmp_iter0);
            if (!(tmp_iter1 < p_arr2.m_len)) {
                abort();
            }
            float* tmp_ref3 = for3_get(&p_arr2, tmp_iter1);
            l_res += i * *tmp_ref2 * *tmp_ref3;
        }
    }
    return l_res;
}

void for3_double(for3_Array* p_arr1) {
    for (size_t tmp_iter0 = for3_iter(); tmp_iter0 < p_arr1->m_len; for3_next(&tmp_iter0)) {
        if (!(tmp_iter0 < p_arr1->m_len)) {
            abort();
        }
        if (*for3_get(p_arr1, tmp_iter0) > 0) {
            if (!(tmp_iter0 < p_arr1->m_len)) {
                abort();
            }
            float* tmp_ref2 = for3_get(p_arr1, tmp_iter0);
            for3_set(p_arr1, tmp_iter0, 2.0f * *tmp_ref2);
            if (!(tmp_iter0 < p_arr1->m_len)) {
                abort();
            }
            float* tmp_ref3 = for3_get(p_arr1, tmp_iter0);
            if (!(tmp_iter0 < p_arr1->m_len)) {
                abort();
            }
            float* tmp_ref4 = for3_get(p_arr1, tmp_iter0);
            *tmp_ref3 += *tmp_ref4;
        }
    }
}

void for3_doSomething(float p_f) {
}

void for3_changeSomehow(float* p_f) {
}

void for3_iterAndChange(for3_Array* p_arr1) {
    for (size_t tmp_iter0 = for3_iter(); tmp_iter0 < p_arr1->m_len; for3_next(&tmp_iter0)) {
        if (!(tmp_iter0 < p_arr1->m_len)) {
            abort();
        }
        float* tmp_ref1 = for3_get(p_arr1, tmp_iter0);
        for3_doSomething(*tmp_ref1);
        if (!(tmp_iter0 < p_arr1->m_len)) {
            abort();
        }
        float* tmp_ref2 = for3_get(p_arr1, tmp_iter0);
        for3_changeSomehow(tmp_ref2);
    }
}
