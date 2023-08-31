#include <minwindef.h>
#include <minwinbase.h>
#include <stringapiset.h>
#include <locale.h>

EXTERN_C DECLSPEC_IMPORT LPWSTR* WINAPI CommandLineToArgvW(LPCWSTR lpCmdLine, int* pNumArgs);
EXTERN_C DECLSPEC_IMPORT LPWSTR WINAPI GetCommandLineW(void);
EXTERN_C DECLSPEC_IMPORT LPSTR WINAPI GetCommandLineA(void);
EXTERN_C DECLSPEC_IMPORT HLOCAL WINAPI LocalAlloc (UINT uFlags, SIZE_T uBytes);
EXTERN_C DECLSPEC_IMPORT HLOCAL WINAPI LocalFree(HLOCAL hMem);


static inline char char_heading_ones(char c) {
    for (char i = 0; i < 8; i++) {
        if (!(c & (1 << (7 - i)))) return i;
    }
    return 8;
}

static inline bool check_utf8_encoding(char* str, size_t len) {
    size_t char_byte_left = 0;
    for (size_t i = 0; i < len; i++) {
        char this_byte = str[i];
        bool is_continuation = this_byte & 0x11000000 == 0x10000000;
        if (char_byte_left) {
            if (!is_continuation) return false;
        } else {
            if (is_continuation) return false;
            char heading_ones = char_heading_ones(this_byte);
            char_byte_left = heading_ones ? heading_ones : 1;
        }
        char_byte_left--;
    }
    return true;
}


static struct MyArgsW {
    wchar_t* basestr;
    int argc;
    wchar_t** argv;
    MyArgsW() {
        setlocale(LC_ALL, "");
        char* ansi_cmdline = GetCommandLineA();
        size_t ansi_cmdline_length = strlen(ansi_cmdline);
        if (check_utf8_encoding(ansi_cmdline, ansi_cmdline_length)) {
            auto required_length = MultiByteToWideChar(CP_UTF8, 0, ansi_cmdline, ansi_cmdline_length, NULL, 0);
            this->basestr = (wchar_t* )malloc(required_length * sizeof(wchar_t));
            MultiByteToWideChar(CP_UTF8, 0, ansi_cmdline, ansi_cmdline_length, this->basestr, required_length);
        } else {
            this->basestr = GetCommandLineW();
        }
        this->argv = CommandLineToArgvW(this->basestr, &this->argc);
    }
    ~MyArgsW() {
        LocalFree(this->argv);
    }
} wargs;

extern "C" {

int get_argc(void) {
    return wargs.argc;
}
wchar_t** get_wargv(void) {
    return wargs.argv;
}

} // extern "C"
