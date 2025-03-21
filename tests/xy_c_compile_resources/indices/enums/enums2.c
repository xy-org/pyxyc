#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct enums2_Color enums2_Color;
typedef struct enums2_PaletteType enums2_PaletteType;

#define ENUMS2_PALETTE (enums2_PaletteType){(enums2_Color){1, 0, 0}, (enums2_Color){0, 2, 0}, (enums2_Color){0, 0, 1}, (enums2_Color){1, 0.647f, 0}, (enums2_Color){1, 1, 1}}

struct enums2_Color {
    float m_r;
    float m_g;
    float m_b;
};
struct enums2_PaletteType {
    enums2_Color m_red;
    enums2_Color m_green;
    enums2_Color m_blue;
    enums2_Color m_orange;
    enums2_Color m_white;
};

void enums2_printColor(enums2_Color p_c) {
}

void enums2_test(void) {
    const enums2_Color l_c1 = {.2f, .2f, 1};
    const enums2_Color l_c2 = ENUMS2_PALETTE.m_blue;
    enums2_printColor(l_c1);
    enums2_printColor(l_c2);
}
