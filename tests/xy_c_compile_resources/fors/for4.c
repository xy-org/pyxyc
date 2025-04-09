#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct for4_Array for4_Array;
typedef struct for4_Slice for4_Slice;
typedef struct for4_SliceIter for4_SliceIter;

struct for4_Array {
    float m_elems[100];
    size_t m_len;
};
struct for4_Slice {
    size_t m_n;
    size_t m_m;
};
struct for4_SliceIter {
    size_t m_i;
    size_t m_lim;
};

for4_Slice for4_slice(size_t p_start, size_t p_end) {
    return (for4_Slice){p_start, p_end};
}

for4_SliceIter for4_iter(for4_Array p_arr, for4_Slice p_slice) {
    return (for4_SliceIter){p_slice.m_n, p_slice.m_m};
}

bool for4_valid(for4_Array p_arr, for4_SliceIter p_iter) {
    return p_iter.m_i < p_arr.m_len && p_iter.m_i < p_iter.m_lim;
}

void for4_next(for4_Array p_arr, for4_SliceIter* p_iter) {
    p_iter->m_i++;
}

float for4_get(for4_Array p_arr, for4_SliceIter p_iter) {
    return p_arr.m_elems[p_iter.m_i];
}

void for4_set(for4_Array p_arr, for4_SliceIter p_iter, float p_val) {
    p_arr.m_elems[p_iter.m_i] = p_val;
}

void for4_calmpTo0(for4_Array* p_arr, size_t p_n, size_t p_m) {
    for4_Slice tmp_0_arg = for4_slice(p_n, p_m);
    for4_SliceIter tmp_1_arg = for4_iter(*p_arr, tmp_0_arg);
    for (for4_SliceIter tmp_2_iter = tmp_1_arg; for4_valid(*p_arr, tmp_2_iter); for4_next(*p_arr, &tmp_2_iter)) {
        if (for4_get(*p_arr, tmp_2_iter) < 0) {
            for4_set(*p_arr, tmp_2_iter, 0.0f);
        }
    }
}
