#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>

typedef int32_t flags_OpenFlags;
typedef struct flags_String flags_String;

#define flags_OpenFlags__readOnly O_RDONLY
#define flags_OpenFlags__writeOnly O_WRONLY
#define flags_OpenFlags__readWrite O_RDWR
#define flags_OpenFlags__append O_APPEND

struct flags_String {
    void* m_addr;
    size_t m_size;
};

flags_String flags_string(void* addr, size_t size) {
    return (flags_String){addr, size};
}

void flags_open(flags_String fn, flags_OpenFlags flags) {
    if (flags & flags_OpenFlags__readWrite) {
    } else if (flags == (flags_OpenFlags__readOnly | flags_OpenFlags__append)) {
    } else if (flags & flags_OpenFlags__readOnly) {
    } else if (flags & flags_OpenFlags__writeOnly) {
    }
}

void flags_testFlags(void) {
    flags_String tmp_arg0 = flags_string("file.txt", 8);
    flags_open(tmp_arg0, flags_OpenFlags__readOnly);
    flags_String tmp_arg1 = flags_string("file.txt", 8);
    flags_open(tmp_arg1, flags_OpenFlags__readOnly);
}
