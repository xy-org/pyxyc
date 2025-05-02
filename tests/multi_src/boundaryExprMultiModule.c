#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct boundaryExprMultiModule_module_Rtti boundaryExprMultiModule_module_Rtti;
typedef struct boundaryExprMultiModule_module_Struct boundaryExprMultiModule_module_Struct;
typedef struct boundaryExprMultiModule_Struct boundaryExprMultiModule_Struct;

struct boundaryExprMultiModule_module_Rtti {
    int32_t m_data;
};
struct boundaryExprMultiModule_module_Struct {
    int32_t m_data;
};
struct boundaryExprMultiModule_Struct {
    int32_t m_value;
};

void boundaryExprMultiModule_module_print(boundaryExprMultiModule_module_Rtti p_rtti) {
}

boundaryExprMultiModule_module_Rtti boundaryExprMultiModule_module_rtti(void) {
    return (boundaryExprMultiModule_module_Rtti){0};
}

boundaryExprMultiModule_module_Rtti boundaryExprMultiModule_rtti(void) {
    return (boundaryExprMultiModule_module_Rtti){0};
}

void boundaryExprMultiModule_main(void) {
    boundaryExprMultiModule_Struct l_x = {0};
    boundaryExprMultiModule_module_print(boundaryExprMultiModule_rtti());
}
