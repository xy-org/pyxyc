#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct donatedArgs5_WithoutDtor donatedArgs5_WithoutDtor;

struct donatedArgs5_WithoutDtor {
    int32_t m_val;
};

void donatedArgs5_action(donatedArgs5_WithoutDtor p_a, void* p_ptr) {
}

void donatedArgs5_test(void) {
    const donatedArgs5_WithoutDtor l_without = {-1};
    donatedArgs5_WithoutDtor tmp_0_addrof = (donatedArgs5_WithoutDtor){0};
    donatedArgs5_action(l_without, &tmp_0_addrof);
    donatedArgs5_WithoutDtor tmp_1_addrof = (donatedArgs5_WithoutDtor){10};
    donatedArgs5_action(l_without, &tmp_1_addrof);
    donatedArgs5_WithoutDtor tmp_2_addrof = (donatedArgs5_WithoutDtor){20};
    donatedArgs5_action(l_without, &tmp_2_addrof);
}
