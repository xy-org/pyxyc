#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>

void* cimport_cstr(void* p_addr, uint64_t p_size) {
    return p_addr;
}

void cimport_main(void) {
    write(0, cimport_cstr((int8_t*)"Hello World\n", 12), 12);
}

int main(int argc, char** argv) {
    cimport_main();
    return 0;
}
