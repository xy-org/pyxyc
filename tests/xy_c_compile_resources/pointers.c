#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void* pointers_pointerFun(void* p_a) {
    int16_t* const l_b = (int16_t*)p_a;
    int16_t* const l_c = l_b + 1;
    uint64_t* const l_d = (uint64_t*)l_c - 2;
    uint64_t* const l_e = l_d;
    return l_e + 3;
}
