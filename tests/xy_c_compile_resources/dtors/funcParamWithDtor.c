#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct funcParamWithDtor_SmallStruct funcParamWithDtor_SmallStruct;
typedef struct funcParamWithDtor_LargeStruct funcParamWithDtor_LargeStruct;

void funcParamWithDtor_fun__SmallStruct(funcParamWithDtor_SmallStruct p_s);
void funcParamWithDtor_fun__LargeStruct(funcParamWithDtor_LargeStruct* p_s);

struct funcParamWithDtor_SmallStruct {
    void* m_ptr;
};
struct funcParamWithDtor_LargeStruct {
    void* m_ptr[10];
};

void funcParamWithDtor_dtor__SmallStruct(funcParamWithDtor_SmallStruct p_s) {
}

void funcParamWithDtor_dtor__LargeStruct(funcParamWithDtor_LargeStruct* p_s) {
}

void funcParamWithDtor_test(void) {
    funcParamWithDtor_SmallStruct l_s1 = {0};
    funcParamWithDtor_LargeStruct l_s2 = {0};
    funcParamWithDtor_fun__SmallStruct(l_s1);
    funcParamWithDtor_fun__LargeStruct(&l_s2);
    funcParamWithDtor_dtor__LargeStruct(&l_s2);
    funcParamWithDtor_dtor__SmallStruct(l_s1);
}

funcParamWithDtor_SmallStruct funcParamWithDtor_mkSmall(void) {
    return (funcParamWithDtor_SmallStruct){0};
}

funcParamWithDtor_LargeStruct funcParamWithDtor_mkLarge(void) {
    return (funcParamWithDtor_LargeStruct){0};
}

void funcParamWithDtor_fun__SmallStruct(funcParamWithDtor_SmallStruct p_s) {
}

void funcParamWithDtor_fun__LargeStruct(funcParamWithDtor_LargeStruct* p_s) {
}
