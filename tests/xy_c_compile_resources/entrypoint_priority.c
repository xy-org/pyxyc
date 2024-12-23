#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

int __xy_sys_argc;
char** __xy_sys_argv;

void entrypoint_priority_main(void) {
    return 0;
}

void entrypoint_priority_moreImportant(void) {
    return 0;
}

int main(int argc, char** argv) {
    __xy_sys_argc = argc;
    __xy_sys_argv = argv;
    entrypoint_priority_moreImportant();
    return 0;
}
