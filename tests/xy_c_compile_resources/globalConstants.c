#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define GLOBALCONSTANTS_C 299792458
#define GLOBALCONSTANTS_PI 3.14
#define GLOBALCONSTANTS_E 2.71828

int32_t globalConstants_func(void) {
    int32_t tmp0 = 0;
    if (GLOBALCONSTANTS_PI > GLOBALCONSTANTS_E) {
        tmp0 = GLOBALCONSTANTS_C;
    } else {
        tmp0 = 0;
    }
    return tmp0;
}
