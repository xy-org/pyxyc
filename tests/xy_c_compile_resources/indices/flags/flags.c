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
        flags_OpenFlags tmp_0 = (flags_OpenFlags){0};
        flags_set(&tmp_0, (flags_OpenFlags){O_RDONLY}, true);
        flags_set(&tmp_0, (flags_OpenFlags){O_APPEND}, true);
        if (p_flags.m_value == tmp_0.m_value) {
        } else if (flags_get(p_flags, (flags_OpenFlags){O_RDONLY})) {
        } else if (flags_get(p_flags, (flags_OpenFlags){O_WRONLY})) {
        }
    }
}

void flags_test1(void) {
    flags_String tmp_0_arg = flags_string((int8_t*)"file.txt", 8);
    flags_open(tmp_0_arg, (flags_OpenFlags){O_RDONLY});
    flags_String tmp_1_arg = flags_string((int8_t*)"file.txt", 8);
    flags_open(tmp_1_arg, (flags_OpenFlags){O_RDONLY});
}

void flags_test2(void) {
    flags_String tmp_0_arg = flags_string((int8_t*)"file.txt", 8);
    flags_open(tmp_0_arg, (flags_OpenFlags){(int32_t)((uint32_t)(flags_OpenFlags){O_RDONLY}.m_value | (uint32_t)(flags_OpenFlags){O_WRONLY}.m_value)});
    flags_String tmp_2_arg = flags_string((int8_t*)"file.txt", 8);
    flags_OpenFlags tmp_1 = (flags_OpenFlags){0};
    flags_set(&tmp_1, (flags_OpenFlags){O_WRONLY}, true);
    flags_set(&tmp_1, (flags_OpenFlags){O_APPEND}, true);
    flags_open(tmp_2_arg, tmp_1);
}

void flags_test3(void) {
    flags_OpenFlags l_flags = {0};
    flags_set(&l_flags, (flags_OpenFlags){O_WRONLY}, true);
    flags_String tmp_0_arg = flags_string((int8_t*)"file.txt", 8);
    flags_open(tmp_0_arg, l_flags);
    flags_String tmp_2_arg = flags_string((int8_t*)"file.txt", 8);
    flags_OpenFlags tmp_1 = l_flags;
    flags_set(&tmp_1, (flags_OpenFlags){O_APPEND}, true);
    flags_open(tmp_2_arg, tmp_1);
    flags_String tmp_4_arg = flags_string((int8_t*)"file.txt", 8);
    flags_OpenFlags tmp_3 = l_flags;
    flags_open(tmp_4_arg, tmp_3);
    flags_String tmp_6_arg = flags_string((int8_t*)"file.txt", 8);
    flags_OpenFlags tmp_5 = (flags_OpenFlags){0};
    flags_set(&tmp_5, (flags_OpenFlags){O_RDONLY}, true);
    flags_open(tmp_6_arg, (flags_OpenFlags){(int32_t)((uint32_t)l_flags.m_value | (uint32_t)tmp_5.m_value)});
}

void flags_test4(flags_OpenFlags p_flags) {
    flags_OpenFlags tmp_0 = (flags_OpenFlags){0};
    flags_set(&tmp_0, (flags_OpenFlags){O_APPEND}, true);
    const flags_OpenFlags l_flags2 = tmp_0;
    flags_String tmp_1_arg = flags_string((int8_t*)"file.txt", 8);
    flags_open(tmp_1_arg, (flags_OpenFlags){(int32_t)((uint32_t)p_flags.m_value | (uint32_t)l_flags2.m_value)});
    flags_String tmp_2_arg = flags_string((int8_t*)"file.txt", 8);
    flags_open(tmp_2_arg, (flags_OpenFlags){(int32_t)((uint32_t)p_flags.m_value & (uint32_t)l_flags2.m_value)});
}
