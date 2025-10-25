#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct paramTags2_Str paramTags2_Str;

struct paramTags2_Str {
    void* m_addr;
    uint64_t m_size;
};

int32_t paramTags2_f1(paramTags2_Str p_s) {
    return -10;
}

int32_t paramTags2_test(void) {
    paramTags2_Str l_s1 = {0};
    paramTags2_Str l_s2 = {0};
    paramTags2_Str l_s3 = {0};
    int32_t tmp_0_arg = paramTags2_f1(l_s1);
    const int32_t l_x = tmp_0_arg + paramTags2_f1(l_s2);
    const int32_t l_y = -20 + 10;
    const int32_t l_z = 20 + paramTags2_f1(l_s3);
    return l_x + l_y + l_z;
}
