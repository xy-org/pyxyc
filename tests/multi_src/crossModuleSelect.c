#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct crossModuleSelect_tag_Test crossModuleSelect_tag_Test;
typedef void (*xy_fp__void)() ;

struct crossModuleSelect_tag_Test {
    char __empty_structs_are_not_allowed_in_c__;
};

void crossModuleSelect_module2_testSomething(void) {
}

void crossModuleSelect_main(void) {
    const xy_fp__void l_tests[1] = {crossModuleSelect_module2_testSomething};
    for (size_t tmp_0_iter = 0; tmp_0_iter < 1; ++tmp_0_iter) {
        l_tests[tmp_0_iter]();
    }
}
