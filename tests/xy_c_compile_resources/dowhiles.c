#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

uint32_t dowhiles_write(int32_t lim) {
    uint32_t __tmp_total0 = 0;
    do {
        __tmp_total0 += dowhiles_step();
    } while (__tmp_total0 < lim);
    return __tmp_total0;
}

int32_t dowhiles_step(void) {
    return 10;
}