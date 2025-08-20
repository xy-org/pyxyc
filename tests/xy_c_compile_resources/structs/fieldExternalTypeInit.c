#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct fieldExternalTypeInit_Data fieldExternalTypeInit_Data;
typedef struct fieldExternalTypeInit_TypeInferenceData fieldExternalTypeInit_TypeInferenceData;

struct fieldExternalTypeInit_Data {
    ptrdiff_t m_ext;
    int32_t m_a;
};
struct fieldExternalTypeInit_TypeInferenceData {
    ptrdiff_t m_ext1;
    ptrdiff_t m_ext2;
};

void fieldExternalTypeInit_test(void) {
    const fieldExternalTypeInit_Data l_data = {(ptrdiff_t){0}, 10};
    const fieldExternalTypeInit_TypeInferenceData l_tiData1 = {(ptrdiff_t){20}, (ptrdiff_t){0}};
    const fieldExternalTypeInit_TypeInferenceData l_tiData2 = {(ptrdiff_t){20}, (ptrdiff_t){30}};
}
