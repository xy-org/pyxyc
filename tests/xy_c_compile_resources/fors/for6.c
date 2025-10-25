#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct for6_Str for6_Str;
typedef struct for6_CharIter for6_CharIter;

void for6_next(for6_Str p_str, for6_CharIter* p_iter);
void for6_doSomething(int32_t p_char);

struct for6_Str {
    int32_t* m_mem;
};
struct for6_CharIter {
    uint64_t m_i;
    int32_t m_char;
};

void for6_dtor(for6_Str p_s) {
}

for6_Str for6_get__Str__Int(for6_Str p_s, int32_t p_i) {
    return (for6_Str){p_s.m_mem + p_i};
}

for6_CharIter for6_chars(for6_Str p_str) {
    for6_CharIter l_iter = {0};
    for6_next(p_str, &l_iter);
    return l_iter;
}

void for6_next(for6_Str p_str, for6_CharIter* p_iter) {
    p_iter->m_i++;
}

void for6_test(void) {
    for6_Str l_s = {0};
    for6_Str tmp_0_arg = for6_get__Str__Int(l_s, 1);
    for6_CharIter tmp_1_arg = for6_chars(tmp_0_arg);
    {
        for (for6_CharIter tmp_2_iter = tmp_1_arg; (int32_t)tmp_2_iter.m_char >= 0; for6_next(tmp_0_arg, &tmp_2_iter)) {
            for6_doSomething(tmp_2_iter.m_char);
        }
        for6_dtor(tmp_0_arg);
        tmp_0_arg = (for6_Str){0};
    }
    for6_dtor(l_s);
}

void for6_doSomething(int32_t p_char) {
}
