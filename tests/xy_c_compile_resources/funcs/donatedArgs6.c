#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct donatedArgs6_WithDtor donatedArgs6_WithDtor;

struct donatedArgs6_WithDtor {
    int32_t m_id;
};

void donatedArgs6_dtor(donatedArgs6_WithDtor p_val) {
}

void donatedArgs6_action(donatedArgs6_WithDtor p_a, donatedArgs6_WithDtor p_b, void* p_ptr) {
}

void donatedArgs6_test(void) {
    donatedArgs6_WithDtor l_val = {-1};
    donatedArgs6_WithDtor tmp_0_arg = (donatedArgs6_WithDtor){0};
    donatedArgs6_action(l_val, tmp_0_arg, &tmp_0_arg);
    donatedArgs6_WithDtor tmp_1_arg = (donatedArgs6_WithDtor){10};
    donatedArgs6_action(l_val, tmp_1_arg, &tmp_1_arg);
    donatedArgs6_WithDtor tmp_2_arg = (donatedArgs6_WithDtor){20};
    donatedArgs6_action(l_val, tmp_2_arg, &tmp_2_arg);
    donatedArgs6_dtor(l_val);
}
