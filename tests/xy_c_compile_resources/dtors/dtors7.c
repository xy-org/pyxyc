#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct dtors7_WithDtor dtors7_WithDtor;
typedef struct dtors7_Container dtors7_Container;

void dtors7_dtor__2(dtors7_Container l_obj);

struct dtors7_WithDtor {
    void* m_mem;
};
struct dtors7_Container {
    dtors7_WithDtor m_wd;
};

void dtors7_dtor(dtors7_WithDtor p_wd) {
}

dtors7_WithDtor dtors7_mkWithDtor(void) {
    return (dtors7_WithDtor){0};
}

void dtors7_doSomething(dtors7_WithDtor p_wd) {
}

void dtors7_test(void) {
    dtors7_Container l_c = {0};
    dtors7_WithDtor l_wd = {0};
    l_wd = dtors7_mkWithDtor();
    dtors7_WithDtor tmp_0_arg = dtors7_mkWithDtor();
    dtors7_doSomething(tmp_0_arg);
    l_c.m_wd = dtors7_mkWithDtor();
    dtors7_dtor(tmp_0_arg);
    dtors7_dtor(l_wd);
    dtors7_dtor__2(l_c);
}

void dtors7_dtor__2(dtors7_Container l_obj) {
    dtors7_dtor(l_obj.m_wd);
    l_obj.m_wd = (dtors7_WithDtor){0};
}
