#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct boundaryExprMultiModule_module_Rtti boundaryExprMultiModule_module_Rtti;
typedef struct boundaryExprMultiModule_module_Struct boundaryExprMultiModule_module_Struct;
typedef struct boundaryExprMultiModule_Struct boundaryExprMultiModule_Struct;

struct boundaryExprMultiModule_module_Rtti {
    char __empty_structs_are_not_allowed_in_c__;
};
struct boundaryExprMultiModule_module_Struct {
    char __empty_structs_are_not_allowed_in_c__;
};
struct boundaryExprMultiModule_Struct {
    char __empty_structs_are_not_allowed_in_c__;
};

void boundaryExprMultiModule_module_print(boundaryExprMultiModule_module_Rtti rtti) {
}

boundaryExprMultiModule_module_Rtti boundaryExprMultiModule_module_rtti(void) {
    return (boundaryExprMultiModule_module_Rtti){0};
}

boundaryExprMultiModule_module_Rtti boundaryExprMultiModule_rtti(void) {
    return (boundaryExprMultiModule_module_Rtti){0};
}

void boundaryExprMultiModule_main(void) {
    boundaryExprMultiModule_Struct x = {0};
    boundaryExprMultiModule_module_print(boundaryExprMultiModule_rtti());
}
