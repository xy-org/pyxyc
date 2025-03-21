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
    bool tmp_arg1 = shortcircuit_func1();
    bool tmp_shortcircuit4 = tmp_arg1;
    if (tmp_shortcircuit4) {
        bool tmp_arg3 = shortcircuit_func1();
        tmp_shortcircuit4 = shortcircuit_func3(tmp_arg3, shortcircuit_func2());
    }
    const bool l_e = tmp_shortcircuit4;
}

void shortcircuit_test4(void) {
    bool tmp_arg0 = shortcircuit_func1();
    bool tmp_arg2 = tmp_arg0 && shortcircuit_func2();
    bool tmp_shortcircuit17 = tmp_arg2;
    if (!tmp_shortcircuit17) {
        bool tmp_arg10 = shortcircuit_func1();
        bool tmp_arg12 = tmp_arg10 || shortcircuit_func2();
        bool tmp_shortcircuit16 = tmp_arg12;
        if (!tmp_shortcircuit16) {
            bool tmp_arg15 = shortcircuit_func1();
            tmp_shortcircuit16 = shortcircuit_func3(tmp_arg15, shortcircuit_func2());
        }
        tmp_shortcircuit17 = tmp_shortcircuit16;
    }
    const bool l_d = tmp_shortcircuit17;
}
