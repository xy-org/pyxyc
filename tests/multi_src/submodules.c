#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int __xy_sys_argc;
char** __xy_sys_argv;

int32_t submodules_sub_callme(void) {
    return 0;
}

int32_t submodules_main(void) {
    return submodules_sub_callme();
}

int main(int argc, char** argv) {
    __xy_sys_argc = argc;
    __xy_sys_argv = argv;
    submodules_main();
    return 0;
}
