#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct forgettingTags2_Data forgettingTags2_Data;

struct forgettingTags2_Data {
    int32_t m_val;
};

void forgettingTags2_work__Int(int32_t p_val) {
}

void forgettingTags2_work__Char(int32_t p_val) {
}

void forgettingTags2_work__Long(int64_t p_val) {
}

void forgettingTags2_test(void) {
    forgettingTags2_Data l_d1 = {0};
    forgettingTags2_Data l_d2 = {0};
    const forgettingTags2_Data l_d3 = l_d2;
    forgettingTags2_work__Long(-1);
    forgettingTags2_work__Int(5);
    forgettingTags2_work__Char('z');
    forgettingTags2_work__Int(5);
    forgettingTags2_work__Long(-1);
}
