#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct callbacks4_Test callbacks4_Test;
typedef struct callbacks4_FuncDesc callbacks4_FuncDesc;
typedef void (*xy_fp__void)() ;

struct callbacks4_Test {
    char __empty_structs_are_not_allowed_in_c__;
};
struct callbacks4_FuncDesc {
    xy_fp__void m_cb;
    void* m_name;
};

void callbacks4_test1(void) {
}

void callbacks4_test2(void) {
}

void* callbacks4_str(void* p_addr, size_t p_size) {
    return p_addr;
}

void callbacks4_test(void) {
    const callbacks4_FuncDesc l_tests[2] = {(callbacks4_FuncDesc){callbacks4_test1, callbacks4_str("test1", 5)}, (callbacks4_FuncDesc){callbacks4_test2, callbacks4_str("test2", 5)}};
}
