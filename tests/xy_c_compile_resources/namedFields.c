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

namedFields_String namedFields_string(void* addr, size_t size) {
    return (namedFields_String){addr, size};
}

void namedFields_test(void) {
    namedFields_Person p1 = {0};
    const namedFields_Person p2 = {0};
    const namedFields_Person p3 = {namedFields_string("Johnny", 6), namedFields_string("Cash", 4)};
    const namedFields_Person p4 = {namedFields_string("Johnny", 6), namedFields_string("Cash", 4), 71, 1.88, true};
    const namedFields_Person p5 = {(namedFields_String){0}, (namedFields_String){0}, 71, 0, true};
    const namedFields_Person p6 = {namedFields_string("Jonny", 5), namedFields_string("Cash", 4), 0, 0, true};
    const namedFields_Person p7 = {namedFields_string("Johnny", 6), namedFields_string("Cash", 4), 71};
    const namedFields_Person p8 = {(namedFields_String){0}, (namedFields_String){0}, 71, 0, 0, (namedFields_Color){0, 0, 0}};
    namedFields_Person tmp0 = p3;
    tmp0.m_age = 71;
    tmp0.m_married = true;
    const namedFields_Person p9 = tmp0;
    namedFields_Person tmp1 = p8;
    tmp1.m_firstName = namedFields_string("Jonny", 5);
    tmp1.m_lastName = namedFields_string("Cash", 4);
    const namedFields_Person p10 = tmp1;
    p1.m_firstName = namedFields_string("Johnny", 6);
    p1.m_age = 71;
    p1.m_height = p4.m_height;
    p1.m_married = true;
}
