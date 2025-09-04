#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void arithmatic1_noop(void) {
}

int32_t arithmatic1_retVal(void) {
    return 0;
}

int32_t arithmatic1_myadd(int32_t p_a, int32_t p_b) {
    return p_a + p_b + arithmatic1_retVal();
}
