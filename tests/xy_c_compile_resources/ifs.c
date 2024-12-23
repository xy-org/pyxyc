#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t ifs_statementLike(int32_t x, int32_t y) {
    if (x < y) {
        return x * y * 3;
    } else {
        return y * 2;
    }
}
