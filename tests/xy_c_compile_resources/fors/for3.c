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

void for3_next(size_t* idx) {
    (*idx)++;
}

float* for3_get(for3_Array* arr, size_t idx) {
    return &arr->m_elems[idx];
}

void for3_set(for3_Array* arr, size_t idx, float elem) {
    arr->m_elems[idx] = elem;
}

float for3_sum(for3_Array arr) {
    float res = 0;
    for (size_t tmp_iter0 = for3_iter(); tmp_iter0 < arr.m_len; for3_next(&tmp_iter0)) {
        if (!(tmp_iter0 < arr.m_len)) {
            abort();
        }
        res += *for3_get(&arr, tmp_iter0);
    }
    return res;
}

float for3_mix(for3_Array arr1, for3_Array arr2) {
    float res = 0;
    {
        uint32_t i = 0;
        size_t tmp_iter0 = for3_iter();
        size_t tmp_iter1 = for3_iter();
        for (; tmp_iter0 < arr1.m_len && tmp_iter1 < arr2.m_len; ++i, for3_next(&tmp_iter0), for3_next(&tmp_iter1)) {
            if (!(tmp_iter0 < arr1.m_len)) {
                abort();
            }
            if (!(tmp_iter1 < arr2.m_len)) {
                abort();
            }
            res += i * *for3_get(&arr1, tmp_iter0) * *for3_get(&arr2, tmp_iter1);
        }
    }
    return res;
}

void for3_double(for3_Array* arr1) {
    for (size_t tmp_iter0 = for3_iter(); tmp_iter0 < arr1->m_len; for3_next(&tmp_iter0)) {
        if (!(tmp_iter0 < arr1->m_len)) {
            abort();
        }
        if (*for3_get(arr1, tmp_iter0) > 0) {
            if (!(tmp_iter0 < arr1->m_len)) {
                abort();
            }
            for3_set(arr1, tmp_iter0, 2.0f * *for3_get(arr1, tmp_iter0));
            if (!(tmp_iter0 < arr1->m_len)) {
                abort();
            }
            if (!(tmp_iter0 < arr1->m_len)) {
                abort();
            }
            float* tmp_ref2 = for3_get(arr1, tmp_iter0);
            *tmp_ref2 += *for3_get(arr1, tmp_iter0);
        }
    }
}

void for3_doSomething(float f) {
}

void for3_changeSomehow(float* f) {
}

void for3_iterAndChange(for3_Array* arr1) {
    for (size_t tmp_iter0 = for3_iter(); tmp_iter0 < arr1->m_len; for3_next(&tmp_iter0)) {
        if (!(tmp_iter0 < arr1->m_len)) {
            abort();
        }
        for3_doSomething(*for3_get(arr1, tmp_iter0));
        if (!(tmp_iter0 < arr1->m_len)) {
            abort();
        }
        for3_changeSomehow(for3_get(arr1, tmp_iter0));
    }
}
