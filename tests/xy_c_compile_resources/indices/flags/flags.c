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

bool flags_get(flags_OpenFlags p_base, flags_OpenFlags p_fields) {
    return (int32_t)((uint32_t)p_base.m_value & (uint32_t)p_fields.m_value) == p_fields.m_value;
}

void flags_set(flags_OpenFlags* p_base, flags_OpenFlags p_fields, bool p_set) {
    p_base->m_value = (int32_t)((uint32_t)p_base->m_value | (uint32_t)(p_fields.m_value * (int32_t)p_set));
}

flags_String flags_string(void* p_addr, size_t p_size) {
    return (flags_String){p_addr, p_size};
}

void flags_open(flags_String p_fn, flags_OpenFlags p_flags) {
    if (flags_get(p_flags, (flags_OpenFlags){O_RDWR})) {
    } else {
        flags_OpenFlags tmp0 = (flags_OpenFlags){0};
        flags_set(&tmp0, (flags_OpenFlags){O_RDONLY}, true);
        flags_set(&tmp0, (flags_OpenFlags){O_APPEND}, true);
        if (p_flags.m_value == tmp0.m_value) {
        } else if (flags_get(p_flags, (flags_OpenFlags){O_RDONLY})) {
        } else if (flags_get(p_flags, (flags_OpenFlags){O_WRONLY})) {
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
    flags_String tmp_arg0 = flags_string("file.txt", 8);
    flags_open(tmp_arg0, (flags_OpenFlags){(int32_t)((uint32_t)(flags_OpenFlags){O_RDONLY}.m_value | (uint32_t)(flags_OpenFlags){O_WRONLY}.m_value)});
    flags_String tmp_arg2 = flags_string("file.txt", 8);
    flags_OpenFlags tmp1 = (flags_OpenFlags){0};
    flags_set(&tmp1, (flags_OpenFlags){O_WRONLY}, true);
    flags_set(&tmp1, (flags_OpenFlags){O_APPEND}, true);
    flags_open(tmp_arg2, tmp1);
}

void flags_test3(void) {
    flags_OpenFlags l_flags = {0};
    flags_set(&l_flags, (flags_OpenFlags){O_WRONLY}, true);
    flags_String tmp_arg0 = flags_string("file.txt", 8);
    flags_open(tmp_arg0, l_flags);
    flags_String tmp_arg2 = flags_string("file.txt", 8);
    flags_OpenFlags tmp1 = l_flags;
    flags_set(&tmp1, (flags_OpenFlags){O_APPEND}, true);
    flags_open(tmp_arg2, tmp1);
    flags_String tmp_arg4 = flags_string("file.txt", 8);
    flags_OpenFlags tmp3 = l_flags;
    flags_open(tmp_arg4, tmp3);
    flags_String tmp_arg6 = flags_string("file.txt", 8);
    flags_OpenFlags tmp5 = (flags_OpenFlags){0};
    flags_set(&tmp5, (flags_OpenFlags){O_RDONLY}, true);
    flags_open(tmp_arg6, (flags_OpenFlags){(int32_t)((uint32_t)l_flags.m_value | (uint32_t)tmp5.m_value)});
}

void flags_test4(flags_OpenFlags p_flags) {
    flags_OpenFlags tmp0 = (flags_OpenFlags){0};
    flags_set(&tmp0, (flags_OpenFlags){O_APPEND}, true);
    const flags_OpenFlags l_flags2 = tmp0;
    flags_String tmp_arg1 = flags_string("file.txt", 8);
    flags_open(tmp_arg1, (flags_OpenFlags){(int32_t)((uint32_t)p_flags.m_value | (uint32_t)l_flags2.m_value)});
    flags_String tmp_arg2 = flags_string("file.txt", 8);
    flags_open(tmp_arg2, (flags_OpenFlags){(int32_t)((uint32_t)p_flags.m_value & (uint32_t)l_flags2.m_value)});
}
