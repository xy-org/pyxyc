#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t splitNamespaces_abs(int32_t p_a) {
    int32_t tmp_1 = 0;
    if (p_a >= 0) {
        tmp_1 = p_a;
    } else {
        tmp_1 = -p_a;
    }
    return tmp_1;
}

void splitNamespaces_test(void) {
    const int32_t l_x = 1;
    const int32_t l_abs = splitNamespaces_abs(l_x);
    const int32_t l_y = splitNamespaces_abs(l_abs) + l_x;
}
