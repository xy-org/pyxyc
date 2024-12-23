#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t dowhiles_simpleDoWhile(int32_t x, int32_t y) {
    int32_t i = 0;
    do {
        x += 10;
        i++;
    } while (x < y);
    return i;
}

int32_t dowhiles_write(int32_t lim) {
    int32_t __tmp_total0 = 0;
    do {
        __tmp_total0 += dowhiles_step();
    } while (__tmp_total0 < lim);
    return __tmp_total0;
}

int32_t dowhiles_step(void) {
    return 10;
}
