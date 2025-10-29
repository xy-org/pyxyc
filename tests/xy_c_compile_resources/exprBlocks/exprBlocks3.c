#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct exprBlocks3_Struct exprBlocks3_Struct;
typedef struct exprBlocks3_Container exprBlocks3_Container;

struct exprBlocks3_Struct {
    int64_t m_val;
};
struct exprBlocks3_Container {
    exprBlocks3_Struct m_s1;
    exprBlocks3_Struct m_s2;
};

void exprBlocks3_fun(exprBlocks3_Struct p_s) {
}

int64_t exprBlocks3_test(exprBlocks3_Struct p_s) {
    int64_t tmp_0_res = 0;
    {
        exprBlocks3_Container l_c = {0};
        tmp_0_res = l_c.m_s1.m_val + l_c.m_s2.m_val;
        {
            exprBlocks3_fun(l_c.m_s1);
            exprBlocks3_fun(l_c.m_s2);
        }
    }
    return tmp_0_res;
}
