#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct donatedArgs2_WithoutDtor donatedArgs2_WithoutDtor;

struct donatedArgs2_WithoutDtor {
    int32_t m_val;
};

void donatedArgs2_action(donatedArgs2_WithoutDtor p_a, donatedArgs2_WithoutDtor p_b) {
}

void donatedArgs2_test(void) {
    const donatedArgs2_WithoutDtor l_without = {0};
    donatedArgs2_action(l_without, l_without);
}
