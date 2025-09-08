#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct globalAndMacro_module1_MyStruct globalAndMacro_module1_MyStruct;
typedef struct xy_GlobalInitData xy_GlobalInitData;
typedef struct xy_Global xy_Global;

void xy_global_init(xy_Global* global, xy_GlobalInitData* data);

#define XY_GLOBALANDMACRO_MODULE1_MYSTRUCT__ID 0

struct globalAndMacro_module1_MyStruct {
    int32_t m_value;
};
struct xy_GlobalInitData {
    globalAndMacro_module1_MyStruct field0;
};
struct xy_Global {
    void* stack[1];
};

__thread xy_GlobalInitData g__xy_globalInitData = {(globalAndMacro_module1_MyStruct){0}};
__thread xy_Global g__xy_globalInstance;
__thread xy_Global* g__xy_global;

void globalAndMacro_module2_test(void) {
    ((globalAndMacro_module1_MyStruct*)g__xy_global->stack[XY_GLOBALANDMACRO_MODULE1_MYSTRUCT__ID])->m_value;
}

void globalAndMacro_callTest(void) {
    globalAndMacro_module2_test();
}

void xy_global_init(xy_Global* global, xy_GlobalInitData* data) {
    global->stack[0] = &data->field0;
}
