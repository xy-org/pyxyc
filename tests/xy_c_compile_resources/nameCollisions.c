#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <errno.h>

typedef struct nameCollisions_ErrnoError nameCollisions_ErrnoError;

struct nameCollisions_ErrnoError {
    int32_t m_errno;
};

