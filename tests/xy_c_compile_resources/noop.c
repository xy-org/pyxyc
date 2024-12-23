#include <stdint.h>

void noop_noop(void) {
}

int32_t noop_retVal(void) {
    return 0;
}

int32_t noop_add(int32_t a, int32_t b) {
    return a + b + noop_retVal();
}
