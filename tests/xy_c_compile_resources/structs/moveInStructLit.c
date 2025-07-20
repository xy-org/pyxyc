#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct moveInStructLit_Data moveInStructLit_Data;

struct moveInStructLit_Data {
    int32_t m_a;
    int64_t m_b;
};

moveInStructLit_Data moveInStructLit_test(int32_t* p_val) {
    int32_t tmp_0_arg = *p_val;
    *p_val = 0;
    const moveInStructLit_Data l_res = {tmp_0_arg, 10000ll};
    return l_res;
}
