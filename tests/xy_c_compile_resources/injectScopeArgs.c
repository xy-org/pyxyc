#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct injectScopeArgs_MyStruct injectScopeArgs_MyStruct;

struct injectScopeArgs_MyStruct {
    int32_t m_a;
    int32_t m_b;
    float m_c;
};

void injectScopeArgs_func(int32_t p_a, float p_b, injectScopeArgs_MyStruct p_c) {
}

void injectScopeArgs_test1(void) {
    const int32_t l_a = 0;
    const float l_b = .0f;
    const injectScopeArgs_MyStruct l_c = {0};
    injectScopeArgs_func(l_a, l_b, l_c);
}

void injectScopeArgs_test2(int32_t p_a, float p_b, injectScopeArgs_MyStruct p_c) {
    injectScopeArgs_func(p_a, p_b, p_c);
}

void injectScopeArgs_test3(float p_b, injectScopeArgs_MyStruct p_c, int32_t p_a) {
    injectScopeArgs_func(p_a, p_b, p_c);
}

void injectScopeArgs_test5(double p_d, injectScopeArgs_MyStruct p_c) {
    const int32_t l_a = p_c.m_a;
    const float l_b = (float)p_c.m_b;
    injectScopeArgs_func(l_a, l_b, p_c);
}
