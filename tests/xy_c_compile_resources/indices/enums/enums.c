#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct enums_Status enums_Status;

struct enums_Status {
    int32_t m_value;
};

void enums_printStatus(enums_Status p_st) {
    if (p_st.m_value == (enums_Status){1}.m_value) {
    } else if (p_st.m_value == (enums_Status){2}.m_value) {
    } else if (p_st.m_value == (enums_Status){4}.m_value) {
    }
}

void enums_testEnums(int32_t p_a) {
    const enums_Status l_orderStatus = {1};
    enums_printStatus(l_orderStatus);
    enums_printStatus((enums_Status){4});
    enums_Status l_st = {2};
    if (p_a > 0) {
        l_st = (enums_Status){4};
    }
    enums_printStatus(l_st);
}
