#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct largeParams2_Large largeParams2_Large;

largeParams2_Large largeParams2_mkLarge(void);

struct largeParams2_Large {
    int32_t m_nums[100];
};

largeParams2_Large largeParams2_mkLarge(void) {
    return (largeParams2_Large){0};
}

void largeParams2_func1(largeParams2_Large* p_a) {
}

void largeParams2_test1(void) {
    largeParams2_Large tmp_0_arg = largeParams2_mkLarge();
    largeParams2_func1(&tmp_0_arg);
}

void largeParams2_test2(void) {
    largeParams2_Large tmp_0_arg = largeParams2_mkLarge();
    largeParams2_func1(&tmp_0_arg);
}
