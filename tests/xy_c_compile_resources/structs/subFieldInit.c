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
}
