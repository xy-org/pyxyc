#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void cmpBools_test(bool a, bool b) {
    const bool c = a == b;
    const bool d = a != b;
    const bool e = !a;
    const bool f = !!a;
    const bool g = a > b;
    const bool h = a >= b;
    const bool i = a < b;
    const bool j = a <= b;
    const bool k = a && b;
    const bool l = a || b;
    const bool m = a - b;
}
