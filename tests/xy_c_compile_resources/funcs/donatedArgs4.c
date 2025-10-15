#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void donatedArgs4_modifyFunc(int32_t p_a) {
    p_a++;
}

void donatedArgs4_testFunc(void) {
    donatedArgs4_modifyFunc(0);
    donatedArgs4_modifyFunc(5 + 10);
}

void donatedArgs4_testMacro(void) {
    int32_t tmp_0_arg = 0;
    {
        tmp_0_arg++;
    }
    int32_t tmp_1_arg = 5 + 10;
    {
        tmp_1_arg++;
    }
}
