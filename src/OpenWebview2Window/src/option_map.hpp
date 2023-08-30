#include <stdbool.h>
#include <unordered_map>
#include <string>


class OptionMapW {
    using woptmap_t = std::unordered_map<std::wstring_view, std::wstring_view>;

private:
    woptmap_t optmap;
    
    void init_my_map(int argc, wchar_t** argv) {
        bool last_is_opt = false;
        const wchar_t *last_arg = NULL;
        
        const wchar_t* option;
        const wchar_t* content;
        
        for(size_t i = 0; i < argc; i++) {
            wchar_t *this_arg = argv[i];
            bool this_is_opt = (wcsncmp(this_arg, L"--", 2) == 0);
            if (last_is_opt) {
                option = last_arg; content = this_is_opt ? L"" : this_arg;
                this->optmap.emplace(std::piecewise_construct,
                    std::forward_as_tuple(option),
                    std::forward_as_tuple(content)
                );
            }
            last_is_opt = this_is_opt;
            last_arg = this_arg;
        }
        if (last_is_opt) {
            option = last_arg; content = L"";
            this->optmap.emplace(std::piecewise_construct,
                std::forward_as_tuple(option),
                std::forward_as_tuple(content)
            );
        }
    }
    
public:
    OptionMapW() = default;
    
    OptionMapW(const OptionMapW& other) = default;
    
    OptionMapW(OptionMapW&& other) {
        this->optmap = std::move(other.optmap);
        other.optmap.clear();
    }
    
    void operator=(const OptionMapW& other) {
        this->optmap = other.optmap;
    }

    void operator=(OptionMapW&& other) {
        this->optmap = std::move(other.optmap);
        other.optmap.clear();
    }

    OptionMapW(int argc, wchar_t** argv) {
        init_my_map(argc, argv);
    }

    bool get_flag(std::wstring_view k) {
        auto opt_kvp_it = this->optmap.find(k);
        if (opt_kvp_it == this->optmap.end()) {
            return false;
        } else {
            return opt_kvp_it->second.empty();
        }
    }

    std::wstring_view get_option (std::wstring_view k) {
        auto opt_kvp_it = this->optmap.find(k);
        if (opt_kvp_it == this->optmap.end()) {
            return std::wstring_view();
        } else {
            return opt_kvp_it->second;
        }
    }
};
