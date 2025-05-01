#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void* escapes_str(void* p_addr, size_t p_size) {
    return p_addr;
}

void escapes_test(void) {
    void* const l_s1 = escapes_str((int8_t*)"\a\b\f\n\r\t\v{}\\\"", 11);
    void* const l_s2 = escapes_str((int8_t*)"\033[ \123 \033[0m \000", 11);
    void* const l_s3 = escapes_str((int8_t*)"\101\304\240\000", 4);
    void* const l_s4 = escapes_str((int8_t*)"\360\237\230\273\360\237\222\230\360\237\253\240", 12);
    void* const l_s5 = escapes_str((int8_t*)"\360\237\230\273\347\210\261\360\237\222\230", 11);
}
