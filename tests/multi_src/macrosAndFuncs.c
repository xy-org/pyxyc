#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct macrosAndFuncs_module1_Struct macrosAndFuncs_module1_Struct;

int32_t macrosAndFuncs_module1_func2(void);
int32_t macrosAndFuncs_module1_func3(void);
int32_t macrosAndFuncs_module1_func1(int32_t p_a, int32_t p_b);

struct macrosAndFuncs_module1_Struct {
    int32_t m_a;
    float m_b;
};

int32_t macrosAndFuncs_module1_func1(int32_t p_a, int32_t p_b) {
    return p_a * p_b;
}

int32_t macrosAndFuncs_module1_func2(void) {
    return 5;
}

int32_t macrosAndFuncs_module1_func3(void) {
    return 10;
}

void macrosAndFuncs_module1_func(void) {
    int32_t tmp_arg0 = macrosAndFuncs_module1_func2();
    macrosAndFuncs_module1_func1(tmp_arg0, macrosAndFuncs_module1_func3());
}

int32_t macrosAndFuncs_func2(void) {
    return 5;
}

int32_t macrosAndFuncs_func1(int32_t p_a, int32_t p_b) {
    return p_a + p_b;
}

int32_t macrosAndFuncs_test(void) {
    macrosAndFuncs_module1_Struct l_my = {0};
    int32_t tmp_arg0 = macrosAndFuncs_func2();
    const int32_t l_a = macrosAndFuncs_func1(tmp_arg0, macrosAndFuncs_func2());
    macrosAndFuncs_module1_Struct tmp1 = l_my;
    int32_t tmp_arg2 = macrosAndFuncs_module1_func2();
    tmp1.m_a = macrosAndFuncs_module1_func1(tmp_arg2, macrosAndFuncs_module1_func3());
    macrosAndFuncs_module1_Struct tmp3 = l_my;
    tmp3.m_b = 0;
    const bool l_x = tmp1.m_a < tmp3.m_a;
    int32_t tmp_arg4 = macrosAndFuncs_func2();
    const int32_t l_b = macrosAndFuncs_func1(tmp_arg4, macrosAndFuncs_func2());
    int32_t tmp_arg5 = macrosAndFuncs_func2();
    const int32_t l_c = macrosAndFuncs_func1(tmp_arg5, macrosAndFuncs_func2());
    return (int32_t)l_x + l_a + l_b + l_c;
}
