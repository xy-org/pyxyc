#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

void embedFile_test(void) {
    void* const s1 = embedFile_str("It's a beautiful day!", 21);
    void* const s2 = embedFile_str("File has 'It's a beautiful day!' as content", 43);
}
