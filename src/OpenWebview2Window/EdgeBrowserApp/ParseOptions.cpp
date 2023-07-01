#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <map>
#include <string>
#define ARGC_MAX 64
#define OPTC_MAX 64

typedef struct warg_t_tag {
    int argc;
    wchar_t** argv;
} warg_t;

typedef std::map<std::wstring, std::wstring> woptmap_t;

warg_t splitwargs(wchar_t* argstr) {
    if (argstr[0] == L'\0') return {0, nullptr};
    
    wchar_t* argv_tmp[ARGC_MAX];
    wchar_t curchr = L'X';
    argv_tmp[0] = argstr; int argidx = 1;
    bool last_is_space = false;
    bool is_in_quotes = false;
    
    for(int i = 0; curchr != L'\0'; i++) {
        curchr = argstr[i];
        if (argidx >= ARGC_MAX) break;
        switch (curchr) {
            case L' ':
                if (last_is_space) break;
                if (is_in_quotes) break;
                argstr[i] = L'\0';
                last_is_space = true;
                break;
            case L'"':
                is_in_quotes = !is_in_quotes;
                argstr[i] = L'\0';
                if (is_in_quotes) {
                    argv_tmp[argidx] = argstr + i + 1;
                    argidx++;
                }
                last_is_space = false;
                break;
            default:
                if (last_is_space) {
                    argv_tmp[argidx] = argstr + i;
                    argidx++;
                }
                last_is_space = false;
        }
    }
    
    int argc = argidx; // argidx++ last time so argc is argidx
    size_t argv_size = argc * sizeof(wchar_t*);
    wchar_t** argv = (wchar_t** )malloc(argv_size);
    memcpy(argv, argv_tmp, argv_size);
    return {argc, argv};
}

woptmap_t warg2optmap(warg_t arg) {
    bool last_is_opt = false;
    wchar_t *last_arg = NULL;
    
    std::wstring option_str;
    std::wstring content_str;
    woptmap_t ret;
    
    for(size_t i = 0; i < arg.argc; i++) {
        wchar_t *this_arg = arg.argv[i];
        bool this_is_opt = (wcsncmp(this_arg, L"--", 2) == 0);
        if (last_is_opt) {
            option_str = last_arg; content_str = this_is_opt ? L"" : this_arg;
            ret.insert(woptmap_t::value_type(option_str, content_str));
        }
        last_is_opt = this_is_opt;
        last_arg = this_arg;
    }
    if (last_is_opt) {
        option_str = last_arg; content_str = L"";
        ret.insert(woptmap_t::value_type(option_str, content_str));
    }

    return ret;
}