#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct donatedArgs1_WithDtor donatedArgs1_WithDtor;

struct donatedArgs1_WithDtor {
    void* m_ptr;
};

void donatedArgs1_dtor(donatedArgs1_WithDtor p_val) {
}

void donatedArgs1_func1(donatedArgs1_WithDtor p_a, donatedArgs1_WithDtor p_b) {
}

void donatedArgs1_test1(void) {
    donatedArgs1_WithDtor l_withA = {0};
    donatedArgs1_WithDtor l_withB = {0};
    donatedArgs1_WithDtor tmp_0_arg = l_withB;
    l_withB = (donatedArgs1_WithDtor){0};
    donatedArgs1_func1(l_withA, tmp_0_arg);
    donatedArgs1_dtor(l_withB);
    donatedArgs1_dtor(l_withA);
}

void donatedArgs1_test2(void) {
    donatedArgs1_WithDtor l_withA = {0};
    donatedArgs1_WithDtor l_withB = {0};
    donatedArgs1_WithDtor tmp_0_arg = (donatedArgs1_WithDtor){0};
    donatedArgs1_func1(l_withA, tmp_0_arg);
    donatedArgs1_dtor(l_withB);
    donatedArgs1_dtor(l_withA);
}
