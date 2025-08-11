#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct unstringing_Str unstringing_Str;

struct unstringing_Str {
    int8_t* m_addr;
    size_t m_size;
};

void unstringing_read(unstringing_Str p_s, size_t* p_i, int32_t* p_val) {
}

void unstringing_test(void) {
    unstringing_Str tmp_0_arg = (unstringing_Str){(int8_t*)"123 456", 7};
    size_t tmp_1_unstr = (size_t)0;
    int32_t l_a = 0;
    unstringing_read(tmp_0_arg, &tmp_1_unstr, &l_a);
    int32_t l_b = 0;
    unstringing_read(tmp_0_arg, &tmp_1_unstr, &l_b);
}
