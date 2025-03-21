#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t splitNamespaces_abs(int32_t p_a) {
    int32_t tmp1 = 0;
    if (p_a >= 0) {
        tmp1 = p_a;
    } else {
        tmp1 = -p_a;
    }
    return tmp1;
}

void splitNamespaces_test(void) {
    const int32_t l_x = 1;
    const int32_t l_abs = splitNamespaces_abs(l_x);
    const int32_t l_y = splitNamespaces_abs(l_abs) + l_x;
}
