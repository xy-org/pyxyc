#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

bool while5_subcond(int32_t p_a, int32_t p_b) {
    return p_a * 10 < p_b;
}

void while5_test(void) {
    int32_t l_i = 0;
    int32_t l_a = 1;
    int32_t l_b = 100;
    if (!(l_a < l_b)) {
        abort();
    }
    bool tmp_0 = 0;
    if (while5_subcond(l_a, l_b)) {
        tmp_0 = true;
    } else {
        tmp_0 = false;
    }
    bool tmp_1_arg = tmp_0 && l_a < 200;
    while (tmp_1_arg) {
        l_a *= 10;
        l_b *= 2;
        l_i++;
        if (!(l_a < l_b)) {
            abort();
        }
        bool tmp_2 = 0;
        if (while5_subcond(l_a, l_b)) {
            tmp_2 = true;
        } else {
            tmp_2 = false;
        }
        tmp_1_arg = tmp_2 && l_a < 200;
    }
}
