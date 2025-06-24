#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct subFieldInit_Color subFieldInit_Color;
typedef struct subFieldInit_Formatting subFieldInit_Formatting;
typedef struct subFieldInit_Effects subFieldInit_Effects;

struct subFieldInit_Color {
    uint8_t m_red;
    uint8_t m_green;
    uint8_t m_blue;
    uint8_t m_alpha;
};
struct subFieldInit_Effects {
    bool m_underline;
    bool m_bold;
};
struct subFieldInit_Formatting {
    subFieldInit_Color m_bg;
    subFieldInit_Color m_fg;
    uint32_t m_fontSize;
    subFieldInit_Effects m_effects;
};

void subFieldInit_test(void) {
    subFieldInit_Formatting tmp_0 = (subFieldInit_Formatting){(subFieldInit_Color){0}, (subFieldInit_Color){0}, 12};
    tmp_0.m_effects.m_bold = true;
    const subFieldInit_Formatting l_a = tmp_0;
    subFieldInit_Formatting tmp_1 = (subFieldInit_Formatting){(subFieldInit_Color){0}, (subFieldInit_Color){0}, 13};
    tmp_1.m_bg.m_red = (uint8_t)255;
    tmp_1.m_fg.m_green = (uint8_t)255;
    tmp_1.m_effects.m_bold = true;
    subFieldInit_Formatting l_b = tmp_1;
    subFieldInit_Formatting tmp_2 = l_b;
    tmp_2.m_effects.m_bold = false;
    tmp_2.m_effects.m_underline = true;
    subFieldInit_Formatting l_c = tmp_2;
    l_b.m_effects.m_bold = true;
    l_b.m_fontSize = 15;
    l_b.m_bg.m_red = l_a.m_bg.m_red;
}
