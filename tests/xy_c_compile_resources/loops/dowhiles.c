#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t dowhiles_step(void);

int32_t dowhiles_simpleDoWhile(int32_t p_x, int32_t p_y) {
    int32_t l_i = 0;
    do {
        p_x += 10;
        l_i++;
    } while (p_x < p_y);
    return l_i;
}

int32_t dowhiles_write(int32_t p_lim) {
    int32_t tmp_total0 = 0;
    do {
        tmp_total0 += dowhiles_step();
    } while (tmp_total0 < p_lim);
    return tmp_total0;
}

int32_t dowhiles_step(void) {
    return 10;
}
