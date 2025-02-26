#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int32_t namedArguments_func__Int__Int__Int(int32_t a, int32_t b, int32_t c) {
    return a + b + c;
}

int32_t namedArguments_func__Int__Int__Int__Int(int32_t a, int32_t b, int32_t c, int32_t d) {
    return a * b * c * d;
}

void namedArguments_testNamedArgs(void) {
    const int32_t a = namedArguments_func__Int__Int__Int(0, 1, 2);
    const int32_t b = namedArguments_func__Int__Int__Int(a, 10, 2);
    const int32_t c = namedArguments_func__Int__Int__Int(b, 1, 10);
    const int32_t d = namedArguments_func__Int__Int__Int(b, 10, c);
    const int32_t e = namedArguments_func__Int__Int__Int(a, b, c);
    const int32_t f = namedArguments_func__Int__Int__Int(a, b, c);
    const int32_t g = namedArguments_func__Int__Int__Int(a, b, c);
    const int32_t h = namedArguments_func__Int__Int__Int(f, b, c);
    const int32_t i = namedArguments_func__Int__Int__Int__Int(1, 2, 3, 4);
    const float j = 5.0f * 1.0f;
}
