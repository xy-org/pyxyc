#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct overloadingCmp_Struct overloadingCmp_Struct;

struct overloadingCmp_Struct {
    int64_t m_val1;
    int64_t m_val2;
};

int32_t overloadingCmp_cmp(overloadingCmp_Struct p_a, overloadingCmp_Struct p_b) {
    if (p_a.m_val1 > p_b.m_val2) {
        return 1;
    }
    if (p_a.m_val1 == p_b.m_val2) {
        return 0;
    }
    return p_a.m_val2 > p_b.m_val1 ? 1 : p_a.m_val2 == p_b.m_val1 ? 0 : -1;
}

void overloadingCmp_test(overloadingCmp_Struct p_x, overloadingCmp_Struct p_y) {
    const bool l_a = overloadingCmp_cmp(p_y, p_x) > 0;
    const bool l_b = overloadingCmp_cmp(p_x, p_y) == 0;
    const bool l_c = overloadingCmp_cmp(p_x, p_y) >= 0;
}
