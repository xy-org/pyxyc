#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t dowhiles_step(void);

int32_t dowhiles_simpleDoWhile(int32_t x, int32_t y) {
    int32_t i = 0;
    do {
        x += 10;
        i++;
    } while (x < y);
    return i;
}

int32_t dowhiles_write(int32_t lim) {
    int32_t tmp_total0 = 0;
    do {
        tmp_total0 += dowhiles_step();
    } while (tmp_total0 < lim);
    return tmp_total0;
}

int32_t dowhiles_step(void) {
    return 10;
}
