#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t dowhile1_step(void);

int32_t dowhile1_simpleDoWhile(int32_t p_x, int32_t p_y) {
    int32_t l_i = 0;
    do {
        p_x += 10;
        l_i++;
    } while (p_x < p_y);
    return l_i;
}

int32_t dowhile1_write(int32_t p_lim) {
    int32_t tmp_0_total = 0;
    do {
        tmp_0_total += dowhile1_step();
    } while (tmp_0_total < p_lim);
    return tmp_0_total;
}

int32_t dowhile1_step(void) {
    return 10;
}
