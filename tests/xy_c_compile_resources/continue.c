#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void continue_test(int32_t p_argc) {
    for (int32_t i = 0; i < p_argc; ++i) {
        if (i == 0) {
            continue;
        }
    }
}
