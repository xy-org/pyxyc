#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct namedFields_Person namedFields_Person;
typedef struct namedFields_String namedFields_String;
typedef struct namedFields_Color namedFields_Color;

struct namedFields_String {
    void* m_addr;
    size_t m_size;
};
struct namedFields_Color {
    uint8_t m_r;
    uint8_t m_g;
    uint8_t m_b;
};
struct namedFields_Person {
    namedFields_String m_firstName;
    namedFields_String m_lastName;
    int32_t m_age;
    double m_height;
    bool m_married;
    namedFields_Color m_favoriteColorClothes;
};

namedFields_String namedFields_string(void* p_addr, size_t p_size) {
    return (namedFields_String){p_addr, p_size};
}

void namedFields_test(void) {
    namedFields_Person l_p1 = {0};
    const namedFields_Person l_p2 = {0};
    const namedFields_Person l_p3 = {namedFields_string("Johnny", 6), namedFields_string("Cash", 4)};
    const namedFields_Person l_p4 = {namedFields_string("Johnny", 6), namedFields_string("Cash", 4), 71, 1.88, true};
    const namedFields_Person l_p5 = {(namedFields_String){0}, (namedFields_String){0}, 71, 0, true};
    const namedFields_Person l_p6 = {namedFields_string("Jonny", 5), namedFields_string("Cash", 4), 0, 0, true};
    const namedFields_Person l_p7 = {namedFields_string("Johnny", 6), namedFields_string("Cash", 4), 71};
    const namedFields_Person l_p8 = {(namedFields_String){0}, (namedFields_String){0}, 71, 0, 0, (namedFields_Color){0, 0, 0}};
    namedFields_Person tmp_0 = l_p3;
    tmp_0.m_age = 71;
    tmp_0.m_married = true;
    const namedFields_Person l_p9 = tmp_0;
    namedFields_Person tmp_1 = l_p8;
    tmp_1.m_firstName = namedFields_string("Jonny", 5);
    tmp_1.m_lastName = namedFields_string("Cash", 4);
    const namedFields_Person l_p10 = tmp_1;
    l_p1.m_firstName = namedFields_string("Johnny", 6);
    l_p1.m_age = 71;
    l_p1.m_height = l_p4.m_height;
    l_p1.m_married = true;
}
