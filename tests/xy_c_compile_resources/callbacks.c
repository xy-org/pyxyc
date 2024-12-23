#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct callbacks_Callback callbacks_Callback;

struct callbacks_Callback {
    char __empty_structs_are_not_allowed_in_c__;
};

int32_t callbacks_test(void) {
}

int32_t callbacks_abs(int32_t a) {
    int32_t tmp1 = 0;
    if (a < 0) {
        tmp1 = a;
    } else {
        tmp1 = a;
    }
    return tmp1;
}
