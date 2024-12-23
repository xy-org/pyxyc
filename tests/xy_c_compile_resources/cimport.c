#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>

void* cimport_cstr(void* addr, size_t size) {
    return addr;
}

int32_t cimport_main(void) {
    write(0, cimport_cstr("Hello World\n", 12), 12);
    return 0;
}

int main(int argc, char** argv) {
    const int res = cimport_main();
    return res;
}
