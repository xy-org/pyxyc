#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct paramTags1_Str paramTags1_Str;

struct paramTags1_Str {
    void* m_addr;
    uint64_t m_size;
};

int32_t paramTags1_f1(paramTags1_Str p_s) {
    return 0;
}

int32_t paramTags1_test(void) {
    paramTags1_Str l_s1 = {0};
    paramTags1_Str l_s2 = {0};
    const int32_t l_x = paramTags1_f1(l_s1);
    const int32_t l_y = 0 + 10;
    return l_x + l_y;
}
