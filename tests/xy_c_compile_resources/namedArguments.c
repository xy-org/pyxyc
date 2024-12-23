#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t namedArguments_func__int__int__int(int32_t a, int32_t b, int32_t c) {
    return a + b + c;
}

int32_t namedArguments_func__int__int__int__int(int32_t a, int32_t b, int32_t c, int32_t d) {
    return a * b * c * d;
}

double namedArguments_func__double__double(double k, double m) {
    return k * m;
}

void namedArguments_testNamedArgs(void) {
    const int32_t a = namedArguments_func__int__int__int(0, 1, 2);
    const int32_t b = namedArguments_func__int__int__int(a, 10, 2);
    const int32_t c = namedArguments_func__int__int__int(b, 1, 10);
    const int32_t d = namedArguments_func__int__int__int(b, 10, c);
    const int32_t e = namedArguments_func__int__int__int(a, b, c);
    const int32_t f = namedArguments_func__int__int__int(a, b, c);
    const int32_t g = namedArguments_func__int__int__int(a, b, c);
    const int32_t h = namedArguments_func__int__int__int(f, b, c);
    const int32_t i = namedArguments_func__int__int__int__int(1, 2, 3, 4);
    const double j = namedArguments_func__double__double(5.0, 1.0);
}
