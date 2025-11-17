#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct callbacks6_FuncDesc callbacks6_FuncDesc;
typedef void (*xy_fp__void)(void) ;
typedef struct callbacks6_Vector callbacks6_Vector;

struct callbacks6_FuncDesc {
    xy_fp__void m_cb;
};
struct callbacks6_Vector {
    void* m_mem;
};

callbacks6_FuncDesc* callbacks6_get(callbacks6_Vector p_v, int32_t p_i) {
    return 0;
}

void callbacks6_test1(callbacks6_FuncDesc p_f) {
    p_f.m_cb();
}

void callbacks6_test2(callbacks6_FuncDesc* p_fs) {
    for (uint64_t tmp_0_iter = 0; tmp_0_iter < 10; ++tmp_0_iter) {
        p_fs[tmp_0_iter].m_cb();
    }
}

void callbacks6_test3(callbacks6_Vector p_v) {
    for (int32_t i = 0; i < 10; ++i) {
        callbacks6_FuncDesc* tmp_0_arg = callbacks6_get(p_v, i);
        tmp_0_arg->m_cb();
    }
}
