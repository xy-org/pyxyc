#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct largeParams_Large largeParams_Large;
typedef struct largeParams_Small largeParams_Small;

struct largeParams_Large {
    int32_t m_nums[100];
};
struct largeParams_Small {
    int32_t m_num;
};

void largeParams_func1(largeParams_Large* p_a, largeParams_Small p_b) {
}

void largeParams_func2(largeParams_Large* p_a, largeParams_Small* p_b) {
}

void largeParams_func3(largeParams_Large* p_a, largeParams_Small p_b) {
}
