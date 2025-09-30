#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define ARRAYCONSTANTS_VALUES (int32_t[4]){1, 2, 3, 4}

int32_t arrayConstants_test(int32_t p_i) {
    return ARRAYCONSTANTS_VALUES[p_i];
}
