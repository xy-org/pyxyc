#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct namedFields_Person namedFields_Person;
typedef struct namedFields_String namedFields_String;
typedef struct namedFields_Color namedFields_Color;

struct namedFields_Person {
    namedFields_String m_firstName;
    namedFields_String m_lastName;
    int32_t m_age;
    double m_height;
    bool m_married;
    namedFields_Color m_favoriteColorClothes;
};
struct namedFields_String {
    void* m_addr;
    size_t m_size;
};
struct namedFields_Color {
    uint8_t m_r;
    uint8_t m_g;
    uint8_t m_b;
};

namedFields_String namedFields_string(void* addr, size_t size) {
    return (namedFields_String){addr, size};
}

void namedFields_test(void) {
    namedFields_Person p1 = (namedFields_Person){0};
}