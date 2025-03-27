#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

bool shortcircuit_func1(void);
bool shortcircuit_func2(void);

bool shortcircuit_func1(void) {
    return false;
}

bool shortcircuit_func2(void) {
    return true;
}

bool shortcircuit_func3(bool p_a, bool p_b) {
    return p_a != p_b;
}

void shortcircuit_test1(bool p_a, bool p_b) {
    const bool l_c = p_b && shortcircuit_func1();
}

void shortcircuit_test2(bool p_a, bool p_b) {
    const bool l_d = p_a || p_b && shortcircuit_func1();
}

void shortcircuit_test3(bool p_a, bool p_b) {
    bool tmp_1_arg = shortcircuit_func1();
    bool tmp_4_shortcircuit = tmp_1_arg;
    if (tmp_4_shortcircuit) {
        bool tmp_3_arg = shortcircuit_func1();
        tmp_4_shortcircuit = shortcircuit_func3(tmp_3_arg, shortcircuit_func2());
    }
    const bool l_e = tmp_4_shortcircuit;
}

void shortcircuit_test4(void) {
    bool tmp_0_arg = shortcircuit_func1();
    bool tmp_2_arg = tmp_0_arg && shortcircuit_func2();
    bool tmp_17_shortcircuit = tmp_2_arg;
    if (!tmp_17_shortcircuit) {
        bool tmp_10_arg = shortcircuit_func1();
        bool tmp_12_arg = tmp_10_arg || shortcircuit_func2();
        bool tmp_16_shortcircuit = tmp_12_arg;
        if (!tmp_16_shortcircuit) {
            bool tmp_15_arg = shortcircuit_func1();
            tmp_16_shortcircuit = shortcircuit_func3(tmp_15_arg, shortcircuit_func2());
        }
        tmp_17_shortcircuit = tmp_16_shortcircuit;
    }
    const bool l_d = tmp_17_shortcircuit;
}
