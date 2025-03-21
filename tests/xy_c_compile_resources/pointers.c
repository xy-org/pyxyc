#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void* pointers_pointerFun(void* p_a) {
    return (int8_t*)p_a + 1;
}
