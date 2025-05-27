#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void dowhile2_test(int32_t* p_lim) {
    do {
        if (*p_lim % 10 == 0) {
            continue;
        }
        if (*p_lim % 100 == 0) {
            break;
        }
        (*p_lim)++;
    } while (*p_lim < 1000);
}
