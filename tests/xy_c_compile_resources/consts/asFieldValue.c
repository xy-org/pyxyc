#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct asFieldValue_Universe asFieldValue_Universe;

#define ASFIELDVALUE_SPEEDOFLIGHT 299792458

struct asFieldValue_Universe {
    int32_t m_c;
};

void asFieldValue_test(void) {
    asFieldValue_Universe l_u = {ASFIELDVALUE_SPEEDOFLIGHT};
}
