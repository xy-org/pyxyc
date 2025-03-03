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

for4_Slice for4_slice(size_t start, size_t end) {
    return (for4_Slice){start, end};
}

for4_SliceIter for4_iter(for4_Array arr, for4_Slice slice) {
    return (for4_SliceIter){slice.m_n, slice.m_m};
}

bool for4_valid(for4_Array arr, for4_SliceIter iter) {
    return iter.m_i < arr.m_len && iter.m_i < iter.m_lim;
}

void for4_next(for4_Array arr, for4_SliceIter* iter) {
    iter->m_i++;
}

float for4_get(for4_Array arr, for4_SliceIter iter) {
    return arr.m_elems[iter.m_i];
}

void for4_set(for4_Array arr, for4_SliceIter iter, float val) {
    arr.m_elems[iter.m_i] = val;
}

void for4_calmpTo0(for4_Array* arr, size_t n, size_t m) {
    for4_Slice tmp_arg0 = for4_slice(n, m);
    for (for4_SliceIter tmp_iter1 = for4_iter(*arr, tmp_arg0); for4_valid(*arr, tmp_iter1); for4_next(*arr, &tmp_iter1)) {
        if (for4_get(*arr, tmp_iter1) < 0) {
            for4_set(*arr, tmp_iter1, 0.0f);
        }
    }
}
