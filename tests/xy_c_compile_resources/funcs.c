#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct funcs_A funcs_A;

funcs_A funcs_rndA(void);
funcs_A funcs_defaultArg1(funcs_A p_a, funcs_A p_b);

struct funcs_A {
    int32_t m_num;
};

funcs_A funcs_double(funcs_A p_a) {
    return (funcs_A){p_a.m_num * 2};
}

void funcs_doubleInout(funcs_A* p_a) {
    p_a->m_num *= 2;
}

funcs_A funcs_callDoubles(funcs_A* p_a) {
    *p_a = funcs_double(*p_a);
    funcs_doubleInout(p_a);
    return *p_a;
}

int32_t funcs_test(void) {
    funcs_A l_a = {5};
    funcs_double(l_a);
    funcs_doubleInout(&l_a);
    return funcs_callDoubles(&l_a).m_num;
}

funcs_A funcs_defaultArg0(funcs_A p_a, funcs_A p_b) {
    return (funcs_A){p_a.m_num + p_b.m_num};
}

funcs_A funcs_defaultArg1(funcs_A p_a, funcs_A p_b) {
    return (funcs_A){p_a.m_num + p_b.m_num};
}

funcs_A funcs_defaultArg2(funcs_A p_a, funcs_A p_b) {
    return (funcs_A){p_a.m_num * p_b.m_num};
}

funcs_A funcs_defaultArg3(funcs_A p_a, funcs_A p_b) {
    return (funcs_A){p_a.m_num - p_b.m_num};
}

funcs_A funcs_rndA(void) {
    return (funcs_A){5};
}

void funcs_testDefaultArgs(void) {
    funcs_defaultArg0((funcs_A){0}, (funcs_A){0});
    funcs_defaultArg1((funcs_A){0}, (funcs_A){0});
    const funcs_A l_a = {10};
    funcs_defaultArg1(l_a, (funcs_A){0});
    funcs_defaultArg2(l_a, funcs_rndA());
    funcs_defaultArg2(l_a, (funcs_A){10});
    funcs_defaultArg3(l_a, funcs_defaultArg1(l_a, (funcs_A){0}));
    funcs_defaultArg3(l_a, (funcs_A){20});
    funcs_A tmp_arg0 = funcs_defaultArg2((funcs_A){0}, funcs_rndA());
    funcs_defaultArg3(tmp_arg0, funcs_defaultArg1(tmp_arg0, (funcs_A){0}));
}
