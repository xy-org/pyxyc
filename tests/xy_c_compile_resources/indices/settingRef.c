#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct settingRef_Array settingRef_Array;

struct settingRef_Array {
    int64_t* m_mem;
    size_t m_size;
};

int64_t* settingRef_get(settingRef_Array p_arr, int32_t p_i) {
    return p_arr.m_mem + p_i;
}

void settingRef_test(settingRef_Array* p_arr) {
    int64_t* tmp_0_arg = settingRef_get(*p_arr, 0);
    *tmp_0_arg = 10ll;
}
