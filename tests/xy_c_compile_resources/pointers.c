#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void* pointers_pointerFun(void* a) {
    return (int8_t*)a + 1;
}
