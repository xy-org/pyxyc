#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct macroBlockDtor_module_Action macroBlockDtor_module_Action;
typedef struct macroBlockDtor_Struct macroBlockDtor_Struct;

struct macroBlockDtor_module_Action {
    int32_t m_code;
};
struct macroBlockDtor_Struct {
    void* m_ptr;
};

void macroBlockDtor_dtor(macroBlockDtor_Struct p_s) {
}

void macroBlockDtor_test(void) {
    macroBlockDtor_module_Action l_a = {0};
    if (l_a.m_code >= 5) {
        macroBlockDtor_Struct l_s = {0};
        macroBlockDtor_dtor(l_s);
    }
}
