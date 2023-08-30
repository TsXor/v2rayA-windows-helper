#include <minwindef.h>
#include <minwinbase.h>
#include <locale.h>

EXTERN_C DECLSPEC_IMPORT LPWSTR* WINAPI CommandLineToArgvW(LPCWSTR lpCmdLine, int* pNumArgs);
EXTERN_C DECLSPEC_IMPORT LPWSTR WINAPI GetCommandLineW(void);
EXTERN_C DECLSPEC_IMPORT LPSTR WINAPI GetCommandLineA(void);
EXTERN_C DECLSPEC_IMPORT HLOCAL WINAPI LocalAlloc (UINT uFlags, SIZE_T uBytes);
EXTERN_C DECLSPEC_IMPORT HLOCAL WINAPI LocalFree(HLOCAL hMem);

static struct MyArgsW {
    wchar_t* basestr;
    int argc;
    wchar_t** argv;
    MyArgsW() {
        setlocale(LC_ALL, "");
        this->basestr = GetCommandLineW();
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
