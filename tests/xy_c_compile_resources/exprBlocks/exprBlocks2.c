#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct exprBlocks2_Struct exprBlocks2_Struct;

struct exprBlocks2_Struct {
    int32_t m_val;
};

void exprBlocks2_func(exprBlocks2_Struct p_s) {
}

void exprBlocks2_dtor(exprBlocks2_Struct p_s) {
}

void exprBlocks2_test(void) {
    exprBlocks2_Struct l_s = {0};
    {
        exprBlocks2_Struct l_s = {10};
        int32_t tmp_0_a = 0;
        {
            tmp_0_a = 10;
        }
        const int32_t l_a = tmp_0_a;
        exprBlocks2_func(l_s);
        exprBlocks2_dtor(l_s);
    }
    exprBlocks2_dtor(l_s);
}
