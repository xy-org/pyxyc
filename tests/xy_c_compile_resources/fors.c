#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void fors_busywait(void) {
    for (size_t i = 0;; ++i) {
        if (i == 10000) {
            break;
        }
    }
}
