#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t splitNamespaces_abs(int32_t a) {
    int32_t tmp1 = 0;
    if (a >= 0) {
        tmp1 = a;
    } else {
        tmp1 = -a;
    }
    return tmp1;
}

void splitNamespaces_test(void) {
    const int32_t x = 1;
    const int32_t abs = splitNamespaces_abs(x);
    const int32_t y = splitNamespaces_abs(abs) + x;
}
