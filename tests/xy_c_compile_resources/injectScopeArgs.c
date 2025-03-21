#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct injectScopeArgs_MyStruct injectScopeArgs_MyStruct;

struct injectScopeArgs_MyStruct {
    int32_t m_a;
    int32_t m_b;
    float m_c;
};

void injectScopeArgs_func(int32_t a, float b, injectScopeArgs_MyStruct c) {
}

void injectScopeArgs_test1(void) {
    const int32_t a = 0;
    const float b = .0f;
    const injectScopeArgs_MyStruct c = {0};
    injectScopeArgs_func(a, b, c);
}

void injectScopeArgs_test2(int32_t a, float b, injectScopeArgs_MyStruct c) {
    injectScopeArgs_func(a, b, c);
}

void injectScopeArgs_test3(float b, injectScopeArgs_MyStruct c, int32_t a) {
    injectScopeArgs_func(a, b, c);
}

void injectScopeArgs_test5(double d, injectScopeArgs_MyStruct c) {
    const int32_t a = c.m_a;
    const int32_t b = c.m_b;
    injectScopeArgs_func(a, b, c);
}
