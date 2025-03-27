#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int __xy_sys_argc;
char** __xy_sys_argv;

int32_t exitWithError_main(void) {
    return 2;
}

int main(int argc, char** argv) {
    __xy_sys_argc = argc;
    __xy_sys_argv = argv;
    const int32_t tmp_0_err = exitWithError_main();
    if ((bool)tmp_0_err) {
        return tmp_0_err;
    }
    return 0;
}
