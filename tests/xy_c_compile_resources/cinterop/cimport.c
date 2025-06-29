#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>

void* cimport_cstr(void* p_addr, size_t p_size) {
    return p_addr;
}

int32_t cimport_main(void) {
    write(0, cimport_cstr((int8_t*)"Hello World\n", 12), 12);
    return 0;
}

int main(int argc, char** argv) {
    cimport_main();
    return 0;
}
