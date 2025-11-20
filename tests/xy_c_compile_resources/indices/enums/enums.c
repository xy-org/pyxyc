#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct enums_Enum enums_Enum;
typedef struct enums_Status enums_Status;

struct enums_Enum {
    int32_t m_value;
};
struct enums_Status {
    int32_t m_value;
};

void enums_printStatus(enums_Status p_st) {
    if (p_st.m_value == (enums_Enum){1}.m_value) {
    } else if (p_st.m_value == (enums_Enum){2}.m_value) {
    } else if (p_st.m_value == (enums_Enum){4}.m_value) {
    }
}

void enums_testEnums(int32_t p_a) {
    enums_Status tmp_0 = (enums_Status){0};
    tmp_0.m_value = (enums_Enum){1}.m_value * true + tmp_0.m_value * !true;
    const enums_Status l_orderStatus = tmp_0;
    enums_printStatus(l_orderStatus);
    enums_Status tmp_1 = (enums_Status){0};
    tmp_1.m_value = (enums_Enum){4}.m_value * true + tmp_1.m_value * !true;
    enums_printStatus(tmp_1);
    enums_Status tmp_2 = (enums_Status){0};
    tmp_2.m_value = (enums_Enum){2}.m_value * true + tmp_2.m_value * !true;
    enums_Status l_st = tmp_2;
    if (p_a > 0) {
        enums_Status tmp_3 = (enums_Status){0};
        tmp_3.m_value = (enums_Enum){4}.m_value * true + tmp_3.m_value * !true;
        l_st = tmp_3;
    }
    enums_printStatus(l_st);
}
