#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct donatedArgs3_WithDtor donatedArgs3_WithDtor;

struct donatedArgs3_WithDtor {
    void* m_ptr;
};

void donatedArgs3_dtor(donatedArgs3_WithDtor p_val) {
}

void donatedArgs3_test1(void) {
    donatedArgs3_WithDtor l_withA = {0};
    donatedArgs3_WithDtor l_withB = {0};
    donatedArgs3_WithDtor tmp_0_arg = l_withB;
    l_withB = (donatedArgs3_WithDtor){0};
    {
        donatedArgs3_dtor(tmp_0_arg);
    }
    donatedArgs3_dtor(l_withB);
    donatedArgs3_dtor(l_withA);
}

void donatedArgs3_test2(void) {
    donatedArgs3_WithDtor l_withA = {0};
    donatedArgs3_WithDtor l_withB = {0};
    donatedArgs3_WithDtor tmp_0_arg = (donatedArgs3_WithDtor){0};
    {
        donatedArgs3_dtor(tmp_0_arg);
    }
    donatedArgs3_dtor(l_withB);
    donatedArgs3_dtor(l_withA);
}
