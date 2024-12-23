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

bool for3_valid(for3_Array arr, size_t idx) {
    return idx < arr.m_len;
}

void for3_next(size_t* idx) {
    (*idx)++;
}

float* for3_get(for3_Array arr, size_t idx) {
    return &arr.m_elems[idx];
}

void for3_set(for3_Array* arr, size_t idx, int32_t elem) {
    arr->m_elems[idx] = elem;
}

float for3_sum(for3_Array arr) {
    float res = 0;
    for (size_t tmp_iter0 = for3_iter(); for3_valid(arr, tmp_iter0); for3_next(&tmp_iter0)) {
        if (!for3_valid(arr, tmp_iter0)) {
            abort();
        }
        res += *for3_get(arr, tmp_iter0);
    }
    return res;
}

float for3_mix(for3_Array arr1, for3_Array arr2) {
    float res = 0;
    {
        uint32_t i = 0;
        size_t tmp_iter0 = for3_iter();
        size_t tmp_iter1 = for3_iter();
        for (; for3_valid(arr1, tmp_iter0) && for3_valid(arr2, tmp_iter1); ++i, for3_next(&tmp_iter0), for3_next(&tmp_iter1)) {
            if (!for3_valid(arr1, tmp_iter0)) {
                abort();
            }
            if (!for3_valid(arr2, tmp_iter1)) {
                abort();
            }
            res += i * *for3_get(arr1, tmp_iter0) * *for3_get(arr2, tmp_iter1);
        }
    }
    return res;
}

void for3_double(for3_Array* arr1) {
    for (size_t tmp_iter0 = for3_iter(); for3_valid(*arr1, tmp_iter0); for3_next(&tmp_iter0)) {
        if (!for3_valid(*arr1, tmp_iter0)) {
            abort();
        }
        if (*for3_get(*arr1, tmp_iter0) > 0) {
            if (!for3_valid(*arr1, tmp_iter0)) {
                abort();
            }
            for3_set(arr1, tmp_iter0, 2.0f * *for3_get(*arr1, tmp_iter0));
            if (!for3_valid(*arr1, tmp_iter0)) {
                abort();
            }
            if (!for3_valid(*arr1, tmp_iter0)) {
                abort();
            }
            float* tmp_ref0 = for3_get(*arr1, tmp_iter0);
            *tmp_ref0 += *for3_get(*arr1, tmp_iter0);
        }
    }
}
