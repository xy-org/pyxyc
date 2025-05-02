#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct package1_module1_Struct1 package1_module1_Struct1;
typedef struct package1_module1_Struct2 package1_module1_Struct2;
typedef struct package2_module1_Struct1 package2_module1_Struct1;
typedef struct package2_module1_Struct2 package2_module1_Struct2;

struct package1_module1_Struct1 {
    int16_t m_data;
};
struct package1_module1_Struct2 {
    int16_t m_data;
};
struct package2_module1_Struct1 {
    int32_t m_data;
};
struct package2_module1_Struct2 {
    int32_t m_data;
};

void package1_module1_test(void) {
    const package1_module1_Struct1 l_a = {0};
    const package1_module1_Struct2 l_b = {0};
}

void package1_module2_test(void) {
    const package1_module1_Struct1 l_a = {0};
}

void package2_test(void) {
    const package1_module1_Struct1 l_a = {0};
    const package2_module1_Struct2 l_b = {0};
}
