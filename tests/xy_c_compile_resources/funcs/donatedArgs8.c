#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct donatedArgs8_WithDtor donatedArgs8_WithDtor;

struct donatedArgs8_WithDtor {
    int32_t* m_ptr;
};

void donatedArgs8_dtor(donatedArgs8_WithDtor p_val) {
}

int32_t donatedArgs8_fun(donatedArgs8_WithDtor p_val) {
    return 0;
}

void donatedArgs8_test1(void) {
    donatedArgs8_WithDtor tmp_0_arg = (donatedArgs8_WithDtor){0};
    donatedArgs8_WithDtor tmp_1_arg = tmp_0_arg;
    donatedArgs8_WithDtor tmp_2_arg = tmp_1_arg;
    donatedArgs8_WithDtor tmp_3_arg = tmp_2_arg;
    const int32_t l_res = donatedArgs8_fun(tmp_3_arg);
}

void donatedArgs8_test2(void) {
    donatedArgs8_WithDtor tmp_0_arg = (donatedArgs8_WithDtor){0};
    donatedArgs8_WithDtor tmp_1_arg = tmp_0_arg;
    donatedArgs8_WithDtor tmp_2_arg = tmp_1_arg;
    const int32_t l_res = donatedArgs8_fun(tmp_2_arg);
}
