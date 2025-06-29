#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct globals2_Struct globals2_Struct;
typedef struct xy_GlobalInitData xy_GlobalInitData;
typedef struct xy_Global xy_Global;

int32_t globals2_test1(void);
int32_t globals2_test2(void);
int32_t globals2_func(globals2_Struct* p_s);
void xy_global_init(xy_Global* global, xy_GlobalInitData* data);

#define XY_GLOBALS2_STRUCT__ID 0

struct globals2_Struct {
    int32_t m_val;
};
struct xy_GlobalInitData {
    globals2_Struct field0;
};
struct xy_Global {
    void* stack[1];
};

__thread xy_GlobalInitData g__xy_globalInitData = {(globals2_Struct){10}};
__thread xy_Global g__xy_globalInstance;
__thread xy_Global* g__xy_global;

int32_t globals2_main(void) {
    const int32_t l_a = globals2_test1();
    const int32_t l_intVal = ((globals2_Struct*)g__xy_global->stack[XY_GLOBALS2_STRUCT__ID])->m_val;
    globals2_Struct l_s = {l_intVal * 2};
    globals2_Struct* tmp_0_gstack = g__xy_global->stack[XY_GLOBALS2_STRUCT__ID];
    g__xy_global->stack[XY_GLOBALS2_STRUCT__ID] = &l_s;
    const int32_t l_b = globals2_test1();
    l_s.m_val++;
    const int32_t l_c = globals2_test2();
    int32_t tmp_1_res = l_a + l_b + l_c;
    g__xy_global->stack[XY_GLOBALS2_STRUCT__ID] = tmp_0_gstack;
    return tmp_1_res;
}

int32_t globals2_test1(void) {
    return ((globals2_Struct*)g__xy_global->stack[XY_GLOBALS2_STRUCT__ID])->m_val;
}

int32_t globals2_test2(void) {
    return globals2_func((globals2_Struct*)g__xy_global->stack[XY_GLOBALS2_STRUCT__ID]);
}

int32_t globals2_func(globals2_Struct* p_s) {
    return p_s->m_val;
}

int main(int argc, char** argv) {
    xy_global_init(&g__xy_globalInstance, &g__xy_globalInitData);
    g__xy_global = &g__xy_globalInstance;
    globals2_main();
    return 0;
}

void xy_global_init(xy_Global* global, xy_GlobalInitData* data) {
    global->stack[0] = &data->field0;
}
