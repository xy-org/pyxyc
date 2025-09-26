#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

double synonym1_sqr(double p_x) {
    return p_x * p_x;
}

double synonym1_test(double p_x) {
    const double l_a = 3.14f;
    const double l_b = 3.14;
    const double l_c = 10;
    return p_x * l_a / l_c * l_b;
}
