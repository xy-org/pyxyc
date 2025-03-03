#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>

int __xy_sys_argc;
char** __xy_sys_argv;

void* cimport_cstr(void* addr, size_t size) {
    return addr;
}

int32_t cimport_main(void) {
    write(0, cimport_cstr("Hello World\n", 12), 12);
    return 0;
}

int main(int argc, char** argv) {
    __xy_sys_argc = argc;
    __xy_sys_argv = argv;
    cimport_main();
    return 0;
}
