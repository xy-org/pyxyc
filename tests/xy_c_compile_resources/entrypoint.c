#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int __xy_sys_argc;
char** __xy_sys_argv;

int32_t entrypoint_main(void) {
    return 0;
}

int main(int argc, char** argv) {
    __xy_sys_argc = argc;
    __xy_sys_argv = argv;
    entrypoint_main();
    return 0;
}
