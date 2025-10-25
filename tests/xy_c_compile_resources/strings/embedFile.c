#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void* embedFile_str(void* p_addr, uint64_t p_size) {
    return p_addr;
}

void embedFile_test(void) {
    void* const l_s1 = embedFile_str((int8_t*)"It's a beautiful day!", 21);
    void* const l_s2 = embedFile_str((int8_t*)"File has 'It's a beautiful day!' as content", 43);
}
