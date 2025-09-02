#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void noop2_noop(void) {
}

int32_t noop2_retVal(void) {
    return 0;
}

int32_t noop2_myadd(int32_t p_a, int32_t p_b) {
    return p_a + p_b + noop2_retVal();
}
