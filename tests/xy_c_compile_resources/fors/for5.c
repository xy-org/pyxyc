#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void for5_mod(int32_t* p_num) {
    *p_num *= 2;
}

void for5_test(void) {
    int32_t l_arr[6] = {1, 3, 5, 7, 9, 11};
    for (size_t tmp_iter0 = 0; tmp_iter0 < 6; ++tmp_iter0) {
        for5_mod(&l_arr[tmp_iter0]);
    }
}
