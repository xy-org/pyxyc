#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct multipleMacros_module1_Struct multipleMacros_module1_Struct;

int32_t multipleMacros_module1_macro1(multipleMacros_module1_Struct s);
bool multipleMacros_module1_macro2(multipleMacros_module1_Struct s1, multipleMacros_module1_Struct s2);

struct multipleMacros_module1_Struct {
    int32_t m_a;
    float m_b;
};

bool multipleMacros_test(void) {
    multipleMacros_module1_Struct my = (multipleMacros_module1_Struct){0};
    return my.m_a < my.m_a;
}
