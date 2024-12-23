#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct funcs_A funcs_A;

struct funcs_A {
    int32_t m_num;
};

funcs_A funcs_double(funcs_A a) {
    return (funcs_A){a.m_num * 2};
}

void funcs_doubleInout(funcs_A* a) {
    a->m_num *= 2;
}

funcs_A funcs_callDoubles(funcs_A* a) {
    *a = funcs_double(*a);
    funcs_doubleInout(a);
    return *a;
}

int32_t funcs_test(void) {
    funcs_A a = (funcs_A){5};
    funcs_double(a);
    funcs_doubleInout(&a);
    return funcs_callDoubles(&a).m_num;
}

funcs_A funcs_defaultArg0(funcs_A a, funcs_A b) {
    return (funcs_A){a.m_num + b.m_num};
}

funcs_A funcs_defaultArg1(funcs_A a, funcs_A b) {
    return (funcs_A){a.m_num + b.m_num};
}

funcs_A funcs_defaultArg2(funcs_A a, funcs_A b) {
    return (funcs_A){a.m_num * b.m_num};
}

funcs_A funcs_rndA(void) {
    return (funcs_A){5};
}

void funcs_testDefaultArgs(void) {
    funcs_defaultArg0((funcs_A){0}, (funcs_A){0});
    funcs_defaultArg1((funcs_A){0}, (funcs_A){0});
    const funcs_A a = (funcs_A){10};
    funcs_defaultArg1(a, (funcs_A){0});
    funcs_defaultArg2(a, funcs_rndA());
}
