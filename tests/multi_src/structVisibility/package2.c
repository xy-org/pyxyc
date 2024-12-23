#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct package1_module1_Struct1 package1_module1_Struct1;
typedef struct package1_module1_Struct2 package1_module1_Struct2;
typedef struct package2_module1_Struct1 package2_module1_Struct1;
typedef struct package2_module1_Struct2 package2_module1_Struct2;

struct package1_module1_Struct1 {
    char __empty_structs_are_not_allowed_in_c__;
};
struct package1_module1_Struct2 {
    char __empty_structs_are_not_allowed_in_c__;
};
struct package2_module1_Struct1 {
    char __empty_structs_are_not_allowed_in_c__;
};
struct package2_module1_Struct2 {
    char __empty_structs_are_not_allowed_in_c__;
};

void package1_module1_test(void) {
    const package1_module1_Struct1 a = (package1_module1_Struct1){0};
    const package1_module1_Struct2 b = (package1_module1_Struct2){0};
}

void package1_module2_test(void) {
    const package1_module1_Struct1 a = (package1_module1_Struct1){0};
}

void package2_test(void) {
    const package1_module1_Struct1 a = (package1_module1_Struct1){0};
    const package2_module1_Struct2 b = (package2_module1_Struct2){0};
}
