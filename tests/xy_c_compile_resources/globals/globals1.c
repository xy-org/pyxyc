#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct globals1_Struct globals1_Struct;
typedef struct xy_GlobalInitData xy_GlobalInitData;
typedef struct xy_Global xy_Global;

int32_t globals1_test1(globals1_Struct p_s);
int32_t globals1_test2(void);
void xy_global_init(xy_Global* global, xy_GlobalInitData* data);

int __xy_sys_argc;
char** __xy_sys_argv;
#define XY_GLOBALS1_STRUCT__ID 0

struct globals1_Struct {
    int32_t m_val;
};
struct xy_GlobalInitData {
    globals1_Struct field0;
};
struct xy_Global {
    void* stack[1];
};

__thread xy_GlobalInitData g__xy_globalInitData = {(globals1_Struct){10}};
__thread xy_Global g__xy_globalInstance;
__thread xy_Global* g__xy_global;

int32_t globals1_main(void) {
    globals1_test1(*(globals1_Struct*)g__xy_global->stack[XY_GLOBALS1_STRUCT__ID]);
    globals1_test2();
    return ((globals1_Struct*)g__xy_global->stack[XY_GLOBALS1_STRUCT__ID])->m_val;
}

int32_t globals1_test1(globals1_Struct p_s) {
    return p_s.m_val;
}

int32_t globals1_test2(void) {
    const globals1_Struct l_s = *(globals1_Struct*)g__xy_global->stack[XY_GLOBALS1_STRUCT__ID];
    return l_s.m_val;
}

int main(int argc, char** argv) {
    xy_global_init(&g__xy_globalInstance, &g__xy_globalInitData);
    g__xy_global = &g__xy_globalInstance;
    __xy_sys_argc = argc;
    __xy_sys_argv = argv;
    globals1_main();
    return 0;
}

void xy_global_init(xy_Global* global, xy_GlobalInitData* data) {
    global->stack[0] = &data->field0;
}
