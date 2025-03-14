#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>

typedef struct flags_OpenFlags flags_OpenFlags;
typedef struct flags_String flags_String;

struct flags_OpenFlags {
    int32_t m_value;
};
struct flags_String {
    void* m_addr;
    size_t m_size;
};

bool flags_get(flags_OpenFlags base, flags_OpenFlags fields) {
    uint32_t tmp_arg0 = (uint32_t)base.m_value;
    uint32_t tmp_arg1 = tmp_arg0 & (uint32_t)fields.m_value;
    return (int32_t)tmp_arg1 == fields.m_value;
}

void flags_set(flags_OpenFlags* base, flags_OpenFlags fields, bool set) {
    int32_t tmp_arg0 = fields.m_value * (int32_t)set;
    uint32_t tmp_arg1 = (uint32_t)base->m_value;
    uint32_t tmp_arg2 = tmp_arg1 | (uint32_t)tmp_arg0;
    base->m_value = (int32_t)tmp_arg2;
}

flags_String flags_string(void* addr, size_t size) {
    return (flags_String){addr, size};
}

void flags_open(flags_String fn, flags_OpenFlags flags) {
    if (flags_get(flags, (flags_OpenFlags){O_RDWR})) {
    } else {
        flags_OpenFlags tmp0 = (flags_OpenFlags){0};
        flags_set(&tmp0, (flags_OpenFlags){O_RDONLY}, true);
        flags_set(&tmp0, (flags_OpenFlags){O_APPEND}, true);
        if (flags.m_value == tmp0.m_value) {
        } else if (flags_get(flags, (flags_OpenFlags){O_RDONLY})) {
        } else if (flags_get(flags, (flags_OpenFlags){O_WRONLY})) {
        }
    }
}

void flags_test1(void) {
    flags_String tmp_arg0 = flags_string("file.txt", 8);
    flags_open(tmp_arg0, (flags_OpenFlags){O_RDONLY});
    flags_String tmp_arg1 = flags_string("file.txt", 8);
    flags_open(tmp_arg1, (flags_OpenFlags){O_RDONLY});
}

void flags_test2(void) {
}
