#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define GLOBALCONSTANTS_C 299792458
#define GLOBALCONSTANTS_PI 3.14
#define GLOBALCONSTANTS_E 2.71828

int32_t globalConstants_fun(void) {
    int32_t tmp_0 = 0;
    if (GLOBALCONSTANTS_PI > GLOBALCONSTANTS_E) {
        tmp_0 = GLOBALCONSTANTS_C;
    } else {
        tmp_0 = 0;
    }
    return tmp_0;
}
