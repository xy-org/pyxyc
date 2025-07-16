#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct subInitFunc_Complex subInitFunc_Complex;

struct subInitFunc_Complex {
    int32_t m_this;
    int32_t m_that;
};

void subInitFunc_dtor(subInitFunc_Complex p_c) {
}

void subInitFunc_setupThis(subInitFunc_Complex* p_c, int32_t p_val) {
    p_c->m_this = p_val;
}

void subInitFunc_setupThat(subInitFunc_Complex* p_c) {
    p_c->m_that += p_c->m_this;
}

void subInitFunc_test(void) {
    subInitFunc_Complex tmp_0 = (subInitFunc_Complex){5, 20};
    subInitFunc_setupThis(&tmp_0, 50);
    subInitFunc_setupThat(&tmp_0);
    subInitFunc_Complex l_a = tmp_0;
    subInitFunc_dtor(l_a);
}
