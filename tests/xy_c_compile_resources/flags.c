#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>

typedef int32_t flags_OpenFlags;
typedef struct flags_String flags_String;

#define flags_OpenFlags__readOnly 1
#define flags_OpenFlags__writeOnly 2
#define flags_OpenFlags__readWrite 4
#define flags_OpenFlags__append 8

struct flags_String {
    void* m_addr;
    size_t m_size;
};

flags_String flags_string(void* addr, size_t size) {
    return (flags_String){addr, size};
}

void flags_open(flags_String fn, flags_OpenFlags flags) {
    if (flags & flags_OpenFlags__readWrite) {
    }
}

void flags_testFlags(void) {
    flags_String tmp_arg0 = flags_string("file.txt", 8);
    flags_open(tmp_arg0, flags_OpenFlags__readOnly);
    flags_String tmp_arg1 = flags_string("file.txt", 8);
    flags_open(tmp_arg1, flags_OpenFlags__readOnly);
    flags_String tmp_arg2 = flags_string("file.txt", 8);
    flags_open(tmp_arg2, flags_OpenFlags__readOnly | flags_OpenFlags__writeOnly);
    flags_String tmp_arg3 = flags_string("file.txt", 8);
    flags_open(tmp_arg3, flags_OpenFlags__writeOnly | flags_OpenFlags__append);
    flags_OpenFlags flags = 0;
    flags |= flags_OpenFlags__writeOnly;
    flags_String tmp_arg4 = flags_string("file.txt", 8);
    flags_open(tmp_arg4, flags);
    flags_String tmp_arg5 = flags_string("file.txt", 8);
    flags_open(tmp_arg5, flags | flags_OpenFlags__append);
    flags_String tmp_arg6 = flags_string("file.txt", 8);
    flags_open(tmp_arg6, flags);
    flags_String tmp_arg7 = flags_string("file.txt", 8);
    flags_open(tmp_arg7, flags | flags_OpenFlags__readOnly);
    const flags_OpenFlags flags2 = flags_OpenFlags__append;
    flags_String tmp_arg8 = flags_string("file.txt", 8);
    flags_open(tmp_arg8, flags | flags2);
    flags_String tmp_arg9 = flags_string("file.txt", 8);
    flags_open(tmp_arg9, flags & flags2);
}
