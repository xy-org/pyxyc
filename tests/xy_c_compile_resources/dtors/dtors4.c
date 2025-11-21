#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct dtors4_Top dtors4_Top;
typedef struct dtors4_Middle dtors4_Middle;
typedef struct dtors4_Bottom dtors4_Bottom;
typedef struct dtors4_Data dtors4_Data;
typedef struct dtors4_Str dtors4_Str;

void dtors4_dtor__5(dtors4_Top l_obj);

struct dtors4_Str {
    int8_t* m_addr;
};
struct dtors4_Data {
    dtors4_Str m_s;
};
struct dtors4_Bottom {
    dtors4_Data m_d;
};
struct dtors4_Middle {
    dtors4_Bottom m_b;
};
struct dtors4_Top {
    dtors4_Middle m_m;
};

void dtors4_dtor(dtors4_Str p_s) {
}

void dtors4_test(void) {
    dtors4_Top l_t = {0};
    dtors4_dtor__5(l_t);
}

void dtors4_dtor__2(dtors4_Data l_obj) {
    dtors4_dtor(l_obj.m_s);
    l_obj.m_s = (dtors4_Str){0};
}

void dtors4_dtor__3(dtors4_Bottom l_obj) {
    dtors4_dtor__2(l_obj.m_d);
    l_obj.m_d = (dtors4_Data){0};
}

void dtors4_dtor__4(dtors4_Middle l_obj) {
    dtors4_dtor__3(l_obj.m_b);
    l_obj.m_b = (dtors4_Bottom){0};
}

void dtors4_dtor__5(dtors4_Top l_obj) {
    dtors4_dtor__4(l_obj.m_m);
    l_obj.m_m = (dtors4_Middle){0};
}
