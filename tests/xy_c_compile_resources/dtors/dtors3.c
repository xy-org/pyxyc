#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct dtors3_Str dtors3_Str;
typedef struct dtors3_Person dtors3_Person;

void dtors3_dtor__2(dtors3_Person* l_obj);

struct dtors3_Str {
    int8_t* m_addr;
};
struct dtors3_Person {
    int32_t m_age;
    dtors3_Str m_name;
    dtors3_Str m_family;
};

void dtors3_dtor(dtors3_Str p_s) {
}

void dtors3_test1(void) {
    dtors3_Person l_p = {0};
    dtors3_dtor__2(&l_p);
}

dtors3_Person dtors3_test2(int32_t p_i) {
    dtors3_Person l_mob[20] = {0};
    dtors3_Person tmp_0_res = l_mob[p_i];
    for (size_t _i = 0; _i < 20; ++_i) {
        dtors3_dtor__2(&l_mob[_i]);
    }
    return tmp_0_res;
}

void dtors3_dtor__2(dtors3_Person* l_obj) {
    dtors3_dtor(l_obj->m_name);
    l_obj->m_name = (dtors3_Str){0};
    dtors3_dtor(l_obj->m_family);
    l_obj->m_family = (dtors3_Str){0};
}
